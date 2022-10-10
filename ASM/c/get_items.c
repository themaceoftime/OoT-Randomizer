#include "get_items.h"

#include "trade_quests.h"
#include "icetrap.h"
#include "item_table.h"
#include "util.h"
#include "z64.h"

extern uint8_t FAST_CHESTS;
extern uint8_t OCARINAS_SHUFFLED;

override_t cfg_item_overrides[512] = { 0 };
int item_overrides_count = 0;

z64_actor_t *dummy_actor = NULL;

// Co-op state
extern uint8_t PLAYER_ID;
extern uint8_t PLAYER_NAME_ID;
extern uint16_t INCOMING_PLAYER;
extern uint16_t INCOMING_ITEM;
extern uint8_t MW_SEND_OWN_ITEMS;
extern override_key_t OUTGOING_KEY;
extern uint16_t OUTGOING_ITEM;
extern uint16_t OUTGOING_PLAYER;

override_t active_override = { 0 };
int active_override_is_outgoing = 0;
item_row_t *active_item_row = NULL;
// Split active_item_row into variables for convenience in ASM
uint32_t active_item_action_id = 0;
uint32_t active_item_text_id = 0;
uint32_t active_item_object_id = 0;
uint32_t active_item_graphic_id = 0;
uint32_t active_item_fast_chest = 0;

uint8_t satisified_pending_frames = 0;

void item_overrides_init() {
    while (cfg_item_overrides[item_overrides_count].key.all != 0) {
        item_overrides_count++;
    }

    // Create an actor satisfying the minimum requirements to give the player an item
    dummy_actor = heap_alloc(sizeof(z64_actor_t));
    dummy_actor->main_proc = (void *)1;
}

override_key_t get_override_search_key(z64_actor_t *actor, uint8_t scene, uint8_t item_id) {
    if (actor->actor_id == 0x0A) {
        // Don't override WINNER purple rupee in the chest minigame scene
        if (scene == 0x10) {
            int chest_item_id = (actor->variable >> 5) & 0x7F;
            if (chest_item_id == 0x75) {
                return (override_key_t){ .all = 0 };
            }
        }

        return (override_key_t){
            .scene = scene,
            .type = OVR_CHEST,
            .flag = actor->variable & 0x1F,
        };
    } else if (actor->actor_id == 0x15) {
        // Only override heart pieces and keys
        int collectable_type = actor->variable & 0xFF;
        if (collectable_type != 0x06 && collectable_type != 0x11) {
            return (override_key_t){ .all = 0 };
        }

        return (override_key_t){
            .scene = scene,
            .type = OVR_COLLECTABLE,
            .flag = *(((uint8_t *)actor) + 0x141),
        };
    } else if (actor->actor_id == 0x19C) {
        return (override_key_t){
            .scene = (actor->variable >> 8) & 0x1F,
            .type = OVR_SKULL,
            .flag = actor->variable & 0xFF,
        };
    } else if (scene == 0x3E && actor->actor_id == 0x011A) {
        return (override_key_t){
            .scene = z64_file.grotto_id,
            .type = OVR_GROTTO_SCRUB,
            .flag = item_id,
        };
    } else {
        return (override_key_t) {
            .scene = scene,
            .type = OVR_BASE_ITEM,
            .flag = item_id,
        };
    }
}

override_t lookup_override_by_key(override_key_t key) {
    int start = 0;
    int end = item_overrides_count - 1;
    while (start <= end) {
        int mid_index = (start + end) / 2;
        override_t mid_entry = cfg_item_overrides[mid_index];
        if (key.all < mid_entry.key.all) {
            end = mid_index - 1;
        } else if (key.all > mid_entry.key.all) {
            start = mid_index + 1;
        } else {
            return mid_entry;
        }
    }
    return (override_t){ 0 };
}

override_t lookup_override(z64_actor_t *actor, uint8_t scene, uint8_t item_id) {
    override_key_t search_key = get_override_search_key(actor, scene, item_id);
    if (search_key.all == 0) {
        return (override_t){ 0 };
    }

    return lookup_override_by_key(search_key);
}

void activate_override(override_t override) {
    uint16_t resolved_item_id = resolve_upgrades(override.value.item_id);
    item_row_t *item_row = get_item_row(resolved_item_id);

    active_override = override;
    if (resolved_item_id == 0xCA)
        active_override_is_outgoing = 2; // Send to everyone
    else
        active_override_is_outgoing = override.value.player != PLAYER_ID;
    active_item_row = item_row;
    active_item_action_id = item_row->action_id;
    active_item_text_id = item_row->text_id;
    active_item_object_id = item_row->object_id;
    active_item_graphic_id = item_row->graphic_id;
    if (override.value.looks_like_item_id) {
        item_row = get_item_row(override.value.looks_like_item_id);
    }
    active_item_fast_chest = item_row->chest_type == BROWN_CHEST || item_row->chest_type == SILVER_CHEST || item_row->chest_type == SKULL_CHEST_SMALL;
    PLAYER_NAME_ID = override.value.player;
}

void clear_override() {
    active_override = (override_t){ 0 };
    active_override_is_outgoing = 0;
    active_item_row = NULL;
    active_item_action_id = 0;
    active_item_text_id = 0;
    active_item_object_id = 0;
    active_item_graphic_id = 0;
    active_item_fast_chest = 0;
}

void set_outgoing_override(override_t *override) {
    if (override->key.type != OVR_DELAYED || override->key.flag != 0xFF) { // don't send items received from incoming back to outgoing
        OUTGOING_KEY = override->key;
        OUTGOING_ITEM = override->value.item_id;
        OUTGOING_PLAYER = override->value.player;
    }
}

void push_pending_item(override_t override) {
    for (int key_scene = 0x30; key_scene < 0x36; key_scene += 2) {
        if (z64_file.scene_flags[key_scene].unk_00_ == 0) {
            z64_file.scene_flags[key_scene].unk_00_ = override.key.all;
            z64_file.scene_flags[key_scene + 1].unk_00_ = override.value.all;
            break;
        }
        if (z64_file.scene_flags[key_scene].unk_00_ == override.key.all) {
            // Prevent duplicate entries
            break;
        }
    }
}

void push_coop_item() {
    if (INCOMING_ITEM != 0) {
        override_t override = { 0 };
        override.key.scene = 0xFF;
        override.key.type = OVR_DELAYED;
        override.key.flag = 0xFF;
        override.value.player = INCOMING_PLAYER;
        override.value.item_id = INCOMING_ITEM;
        push_pending_item(override);
    }
}

void push_delayed_item(uint8_t flag) {
    override_key_t search_key = { .all = 0 };
    search_key.scene = 0xFF;
    search_key.type = OVR_DELAYED;
    search_key.flag = flag;
    override_t override = lookup_override_by_key(search_key);
    if (override.key.all != 0) {
        push_pending_item(override);
    }
}

void pop_pending_item() {
    for (int scene = 0x30; scene < 0x34; scene++) {
        z64_file.scene_flags[scene].unk_00_ = z64_file.scene_flags[scene + 2].unk_00_;
    }
    z64_file.scene_flags[0x34].unk_00_ = 0;
    z64_file.scene_flags[0x35].unk_00_ = 0;
}

void after_key_received(override_key_t key) {
    if (key.type == OVR_DELAYED && key.flag == 0xFF) {
        INCOMING_ITEM = 0;
        INCOMING_PLAYER = 0;
        uint16_t *received_item_counter = (uint16_t *)(z64_file_addr + 0x90);
        (*received_item_counter)++;
        return;
    }

    override_key_t fire_arrow_key = {
        .scene = 0x57, // Lake hylia
        .type = OVR_BASE_ITEM,
        .flag = 0x58, // Fire arrows item ID
    };
    if (key.all == fire_arrow_key.all) {
        // Mark fire arrow location as obtained
        z64_game.chest_flags |= 0x1;
    }
}

void pop_ice_trap() {
    override_key_t key = { .all = z64_file.scene_flags[0x30].unk_00_ };
    override_value_t value = { .all = z64_file.scene_flags[0x31].unk_00_ };
    if (value.item_id == 0x7C && value.player == PLAYER_ID) {
        push_pending_ice_trap();
        pop_pending_item();
        after_key_received(key);
    }
}

void after_item_received() {
    override_key_t key = active_override.key;
    if (key.all == 0) {
        return;
    }

    if (MW_SEND_OWN_ITEMS || active_override_is_outgoing) {
        set_outgoing_override(&active_override);
    }

    if (key.all == z64_file.scene_flags[0x30].unk_00_) {
        pop_pending_item();
    }
    after_key_received(key);
    clear_override();
}

inline uint32_t link_is_ready() {
    if ((z64_link.state_flags_1 & 0xFCAC2485) == 0 &&
        (z64_link.common.unk_flags_00 & 0x0001) &&
        (z64_link.state_flags_2 & 0x000C0000) == 0 &&
        (z64_event_state_1 & 0x20) == 0 &&
        (z64_game.camera_2 == 0)) {
        satisified_pending_frames++;
    }
    else {
        satisified_pending_frames = 0;
    }
    if (satisified_pending_frames >= 2) {
        satisified_pending_frames = 0;
        return 1;
    }
    return 0;
}

void try_pending_item() {
    override_t override = {
        .key.all = z64_file.scene_flags[0x30].unk_00_,
        .value.all = z64_file.scene_flags[0x31].unk_00_,
    };

    if(override.key.all == 0) {
        return;
    }

    if (override.value.item_id == 0xCA && override.value.player != PLAYER_ID) {
        uint16_t resolved_item_id = resolve_upgrades(override.value.item_id);
        item_row_t *item_row = get_item_row(resolved_item_id);
        call_effect_function(item_row);
        pop_pending_item();
        after_key_received(override.key);
        clear_override();
        return;
    }

    activate_override(override);

    z64_link.incoming_item_actor = dummy_actor;
    z64_link.incoming_item_id = active_item_row->base_item_id;
}

void handle_pending_items() {
    push_coop_item();
    if (link_is_ready()) {
        pop_ice_trap();
        // don't apply ice traps while playing the treasure chest game, since that would allow cheesing it
        // (dying there lets you buy another key but doesn't lock already unlocked doors)
        if (ice_trap_is_pending() && (z64_game.scene_index != 0x0010 || z64_game.chest_flags & 0x00000400)) {
            give_ice_trap();
        } else {
            try_pending_item();
        }
    }
}

void get_item(z64_actor_t *from_actor, z64_link_t *link, int8_t incoming_item_id) {
    override_t override = { 0 };
    int incoming_negative = incoming_item_id < 0;

    if (from_actor && incoming_item_id != 0) {
        int8_t item_id = incoming_negative ? -incoming_item_id : incoming_item_id;
        // Remove turned in trade items from player inventory. The incoming item
        // ID will be the next sequential trade item, so use that as a reference.
        item_row_t *row = get_item_row(item_id);
        if (row) {
            int16_t action_id = row->action_id;
            if (CFG_ADULT_TRADE_SHUFFLE && action_id > 0 && from_actor->actor_id != 0x0A && IsAdultTradeItem(action_id)) {
                if (action_id == Z64_ITEM_BIGGORON_SWORD) {
                    TurnInTradeItem(Z64_ITEM_CLAIM_CHECK);
                } else {
                    TurnInTradeItem(action_id - 1);
                }
            }
        }
        override = lookup_override(from_actor, z64_game.scene_index, item_id);
    }

    if (override.key.all == 0) {
        // No override, use base game's item code
        clear_override();
        link->incoming_item_id = incoming_item_id;
        return;
    }

    activate_override(override);
    int8_t base_item_id = active_item_row->base_item_id;

    if (from_actor->actor_id == 0x0A) {
        // Update chest contents
        if (override.value.item_id == 0x7C && override.value.player == PLAYER_ID && (FAST_CHESTS || active_item_fast_chest)) {
            // Use ice trap base item ID to freeze Link as the chest opens rather than playing the full item get animation
            base_item_id = 0x7C;
        }
        from_actor->variable = (from_actor->variable & 0xF01F) | (base_item_id << 5);
    }


    link->incoming_item_id = incoming_negative ? -base_item_id : base_item_id;
}

void get_skulltula_token(z64_actor_t *token_actor) {
    override_t override = lookup_override(token_actor, 0, 0);
    uint16_t item_id;
    uint8_t player;
    if (override.key.all == 0) {
        // Give a skulltula token if there is no override
        item_id = 0x5B;
        player = PLAYER_ID;
    } else {
        item_id = override.value.item_id;
        player = override.value.player;
    }

    uint16_t resolved_item_id = resolve_upgrades(item_id);
    item_row_t *item_row = get_item_row(resolved_item_id);

    token_actor->draw_proc = NULL;

    PLAYER_NAME_ID = player;
    z64_DisplayTextbox(&z64_game, item_row->text_id, 0);

    if (resolved_item_id == 0xCA) {
        // Send triforce to everyone
        set_outgoing_override(&override);
        z64_GiveItem(&z64_game, item_row->action_id);
        call_effect_function(item_row);
    } else if (player != PLAYER_ID) {
        set_outgoing_override(&override);
    } else {
        if (MW_SEND_OWN_ITEMS) {
            set_outgoing_override(&override);
        }
        z64_GiveItem(&z64_game, item_row->action_id);
        call_effect_function(item_row);
    }
}

int give_sarias_gift() {
    uint16_t received_sarias_gift = (z64_file.event_chk_inf[0x0C] & 0x0002);
    if (received_sarias_gift == 0) {
        if (OCARINAS_SHUFFLED)
            push_delayed_item(0x02);
        z64_file.event_chk_inf[0x0C] |= 0x0002;
    }

    // return 1 to skip the cutscene
    return OCARINAS_SHUFFLED || received_sarias_gift;
}
