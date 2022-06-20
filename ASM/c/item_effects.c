#include "item_effects.h"
#include "dungeon_info.h"
#include "save.h"
#define rupee_cap ((uint16_t*)0x800F8CEC)
volatile uint8_t MAX_RUPEES = 0;

typedef void (*commit_scene_flags_fn)(z64_game_t* game_ctxt);
#define commit_scene_flags ((commit_scene_flags_fn)0x8009D894)
typedef void (*save_game_fn)(void* unk);
#define save_game ((save_game_fn)0x800905D4)

void no_effect(z64_file_t *save, int16_t arg1, int16_t arg2) {
}

void full_heal(z64_file_t *save, int16_t arg1, int16_t arg2) {
    save->refill_hearts = 20 * 0x10;
}

void give_triforce_piece(z64_file_t *save, int16_t arg1, int16_t arg2) {
    save->scene_flags[0x48].unk_00_ += 1; //Unused word in scene x48.
    set_triforce_render();

    // Trigger win when the target is hit
    if (save->scene_flags[0x48].unk_00_ == TRIFORCE_PIECES_REQUIRED) {
        // Give GC boss key to allow beating the game again afterwards
        give_dungeon_item(save, 0x01, 10);

        // Save Game
        save->entrance_index = z64_game.entrance_index;
        save->scene_index = z64_game.scene_index;
        commit_scene_flags(&z64_game);
        save_game(&z64_game + 0x1F74);

        // warp to start of credits sequence
        z64_file.cutscene_next = 0xFFF8;
        z64_game.entrance_index = 0x00A0;
        z64_game.scene_load_flag = 0x14;
        z64_game.fadeout_transition = 0x01;
    }
}

void give_tycoon_wallet(z64_file_t *save, int16_t arg1, int16_t arg2) {
    save->wallet = 3;
    if(MAX_RUPEES)
        save->rupees = rupee_cap[arg1];
}

void give_biggoron_sword(z64_file_t *save, int16_t arg1, int16_t arg2) {
    save->bgs_flag = 1; // Set flag to make the sword durable
}

void give_bottle(z64_file_t *save, int16_t bottle_item_id, int16_t arg2) {
    for (int i = Z64_SLOT_BOTTLE_1; i <= Z64_SLOT_BOTTLE_4; i++) {
        if (save->items[i] == -1) {
            save->items[i] = bottle_item_id;
            return;
        }
    }
}

void give_dungeon_item(z64_file_t *save, int16_t mask, int16_t dungeon_id) {
    save->dungeon_items[dungeon_id].items |= mask;
}

char key_counts[14][2] = {
    {0, 0}, // Deku Tree
    {0, 0}, // Dodongo's Cavern
    {0, 0}, // Inside Jabu Jabu's Belly
    {5, 6}, // Forest Temple
    {8, 5}, // Fire Temple
    {6, 2}, // Water Temple
    {5, 7}, // Spirit Temple
    {5, 6}, // Shadow Temple
    {3, 2}, // Bottom of the Well
    {0, 0}, // Ice Cavern
    {0, 0}, // Ganon's Tower
    {9, 3}, // Gerudo Training Ground
    {4, 4}, // Thieves' Hideout
    {2, 3}, // Ganon's Castle
};

void give_small_key(z64_file_t *save, int16_t dungeon_id, int16_t arg2) {
    int8_t current_keys = save->dungeon_keys[dungeon_id] > 0 ? save->dungeon_keys[dungeon_id] : 0;
    save->dungeon_keys[dungeon_id] = current_keys + 1;
    int8_t total_keys = save->scene_flags[dungeon_id].unk_00_;
    save->scene_flags[dungeon_id].unk_00_ = total_keys + 1;
}

void give_small_key_ring(z64_file_t *save, int16_t dungeon_id, int16_t arg2) {
    int8_t current_keys = save->dungeon_keys[dungeon_id] > 0 ? save->dungeon_keys[dungeon_id] : 0;
    save->dungeon_keys[dungeon_id] = current_keys + key_counts[dungeon_id][CFG_DUNGEON_IS_MQ[dungeon_id]];
    int8_t total_keys = save->scene_flags[dungeon_id].unk_00_;
    save->scene_flags[dungeon_id].unk_00_ = total_keys + key_counts[dungeon_id][CFG_DUNGEON_IS_MQ[dungeon_id]];
}



silver_rupee_data_t silver_rupee_vars[0x16][2] = {
    //Vanilla,   Master Quest
    {{-1, 0xFF}, { 5, 0x1F}}, // Dodongos Cavern Staircase. Patched to use switch flag 0x1F
    {{ 5, 0x08}, {-1, 0xFF}}, // Ice Cavern Spinning Scythe
    {{ 5, 0x09}, {-1, 0xFF}}, // Ice Cavern Push Block
    {{ 5, 0x1F}, {-1, 0xFF}}, // Bottom of the Well Basement
    {{ 5, 0x01}, { 5, 0x01}}, // Shadow Temple Scythe Shortcut
    {{-1, 0xFF}, {10, 0x03}}, // Shadow Temple Invisible Blades
    {{ 5, 0x09}, { 5, 0x11}}, // Shadow Temple Huge Pit
    {{ 5, 0x08}, {10, 0x08}}, // Shadow Temple Invisible Spikes
    {{ 5, 0x1C}, { 5, 0x1C}}, // Gerudo Training Ground Slopes
    {{ 5, 0x0C}, { 6, 0x0C}}, // Gerudo Training Ground Lava
    {{ 5, 0x1B}, { 3, 0x1B}}, // Gerudo Training Ground Water
    {{ 5, 0x05}, {-1, 0xFF}}, // Spirit Temple Child Early Torches
    {{ 5, 0x02}, {-1, 0xFF}}, // Spirit Temple Adult Boulders
    {{-1, 0xFF}, { 5, 0x1F}}, // Spirit Temple Lobby and Lower Adult. Patched to use switch flag 0x1F
    {{ 5, 0x0A}, {-1, 0xFF}}, // Spirit Temple Sun Block
    {{-1, 0xFF}, { 5, 0x00}}, // Spirit Temple Adult Climb
    {{ 5, 0x0B}, {-1, 0xFF}}, // Ganons Castle Spirit Trial
    {{ 5, 0x12}, {-1, 0xFF}}, // Ganons Castle Light Trial
    {{ 5, 0x09}, { 5, 0x01}}, // Ganons Castle Fire Trial
    {{-1, 0xFF}, { 5, 0x1B}}, // Ganons Castle Shadow Trial
    {{-1, 0xFF}, { 5, 0x02}}, // Ganons Castle Water Trial
    {{ 5, 0x0E}, {-1, 0xFF}}, // Ganons Castle Forest Trial
};

void give_silver_rupee(z64_file_t *save, int16_t dungeon_id, int16_t silver_rupee_id) {
    silver_rupee_data_t var = silver_rupee_vars[silver_rupee_id][CFG_DUNGEON_IS_MQ[dungeon_id]];

    if (extended_savectx.silver_rupee_counts[silver_rupee_id] == var.needed_count) return;
    extended_savectx.silver_rupee_counts[silver_rupee_id]++;

    if (extended_savectx.silver_rupee_counts[silver_rupee_id] == var.needed_count) {
        if (silver_rupee_id == 8) { // GTG Boulder room needs to set room clear flag as well in order to make the timer go away. Maybe others?
            if (z64_game.scene_index == dungeon_id)
            {
                z64_game.clear_flags |= 1 << 2;
                z64_game.temp_clear_flags |= 1 << 2;
            }
            else
            {
                save->scene_flags[dungeon_id].clear |= 1 << 2;
            }
        }
        if (z64_game.scene_index == dungeon_id)
            z64_game.swch_flags |= 1 << var.switch_flag;
        else
            save->scene_flags[dungeon_id].swch |= 1 << var.switch_flag;
    }
}

void give_silver_rupee_pouch(z64_file_t *save, int16_t dungeon_id, int16_t silver_rupee_id) {
    silver_rupee_data_t var = silver_rupee_vars[silver_rupee_id][CFG_DUNGEON_IS_MQ[dungeon_id]];

    if (extended_savectx.silver_rupee_counts[silver_rupee_id] == var.needed_count) return;
    extended_savectx.silver_rupee_counts[silver_rupee_id] = var.needed_count;

    if (silver_rupee_id == 7) { // GTG Boulder room needs to set room clear flag as well in order to make the timer go away. Maybe others?
        if (z64_game.scene_index == dungeon_id)
            z64_game.clear_flags |= 1 << 2;
        else
            save->scene_flags[dungeon_id].clear |= 1 << 2;
    }
    if (z64_game.scene_index == dungeon_id)
        z64_game.swch_flags |= 1 << var.switch_flag;
    else
        save->scene_flags[dungeon_id].swch |= 1 << var.switch_flag;
}

void give_defense(z64_file_t *save, int16_t arg1, int16_t arg2) {
    save->double_defense = 1;
    save->defense_hearts = 20;
    save->refill_hearts = 20 * 0x10;
}

void give_magic(z64_file_t *save, int16_t arg1, int16_t arg2) {
    save->magic_capacity_set = 1; // Set meter level
    save->magic_acquired = 1; // Required for meter to persist on save load
    save->magic_meter_size = 0x30; // Set meter size
    save->magic = 0x30; // Fill meter
}

void give_double_magic(z64_file_t *save, int16_t arg1, int16_t arg2) {
    save->magic_capacity_set = 2; // Set meter level
    save->magic_acquired = 1; // Required for meter to persist on save load
    save->magic_capacity = 1; // Required for meter to persist on save load
    save->magic_meter_size = 0x60; // Set meter size
    save->magic = 0x60; // Fill meter
}

void give_fairy_ocarina(z64_file_t *save, int16_t arg1, int16_t arg2) {
    save->items[Z64_SLOT_OCARINA] = 0x07;
}

void give_song(z64_file_t *save, int16_t quest_bit, int16_t arg2) {
    save->quest_items |= 1 << quest_bit;
}

void ice_trap_effect(z64_file_t *save, int16_t arg1, int16_t arg2) {
    push_pending_ice_trap();
}

void give_bean_pack(z64_file_t *save, int16_t arg1, int16_t arg2) {
    save->items[Z64_SLOT_BEANS] = Z64_ITEM_BEANS;
    save->ammo[14] += 10; // 10 Magic Beans
}

void fill_wallet_upgrade(z64_file_t *save, int16_t arg1, int16_t arg2) {
    if(MAX_RUPEES)
        save->rupees = rupee_cap[arg1];
}

void clear_excess_hearts(z64_file_t *save, int16_t arg1, int16_t arg2) {
    if (save->energy_capacity >= 19 * 0x10)  // Giving a Heart Container at 19 hearts.
        save->heart_pieces = 0;
    save->refill_hearts = 20 * 0x10;
}

uint8_t OPEN_KAKARIKO = 0;
uint8_t COMPLETE_MASK_QUEST = 0;
void open_mask_shop(z64_file_t *save, int16_t arg1, int16_t arg2) {
    if (OPEN_KAKARIKO) {
        save->inf_table[7] = save->inf_table[7] | 0x40; // "Spoke to Gate Guard About Mask Shop"
        if (!COMPLETE_MASK_QUEST) {
            save->item_get_inf[2] = save->item_get_inf[2] & 0xFB87; // Unset "Obtained Mask" flags just in case of savewarp before Impa.
        }
    }
    if (COMPLETE_MASK_QUEST) {
        save->inf_table[7] = save->inf_table[7] | 0x80; // "Soldier Wears Keaton Mask"
        save->item_get_inf[3] = save->item_get_inf[3] | 0x8F00; // "Sold Masks & Unlocked Masks" / "Obtained Mask of Truth"
        save->event_chk_inf[8] = save->event_chk_inf[8] | 0xF000; // "Paid Back Mask Fees"
    }
}
