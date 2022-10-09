#include <stdbool.h>
#include "dungeon_info.h"
#include "gfx.h"
#include "text.h"
#include "z64.h"
#include "trade_quests.h"
#include "dpad.h"

typedef struct {
    uint8_t index;
    struct {
        uint8_t has_keys : 1;
        uint8_t has_boss_key : 1;
        uint8_t has_card : 1;
        uint8_t has_map : 1;
    };
    uint8_t skulltulas;
    char name[10];
} dungeon_entry_t;

dungeon_entry_t dungeons[] = {
    {  0, 0, 0, 0, 1, 0x0F, "Deku"    },
    {  1, 0, 0, 0, 1, 0x1F, "Dodongo" },
    {  2, 0, 0, 0, 1, 0x0F, "Jabu"    },

    {  3, 1, 1, 0, 1, 0x1F, "Forest"  },
    {  4, 1, 1, 0, 1, 0x1F, "Fire"    },
    {  5, 1, 1, 0, 1, 0x1F, "Water"   },
    {  7, 1, 1, 0, 1, 0x1F, "Shadow"  },
    {  6, 1, 1, 0, 1, 0x1F, "Spirit"  },

    {  8, 1, 0, 0, 1, 0x07, "BotW"    },
    {  9, 0, 0, 0, 1, 0x07, "Ice"     },
    { 12, 1, 0, 1, 0, 0x00, "Hideout" },
    { 11, 1, 0, 0, 0, 0x00, "GTG"     },
    { 13, 1, 1, 0, 0, 0x00, "Ganon"   },
};

int dungeon_count = 13;

typedef struct {
    uint8_t idx;
    uint8_t r;
    uint8_t g;
    uint8_t b;
} medal_t;

medal_t medals[] = {
    { 5, 0xC8, 0xC8, 0x00 }, // Light
    { 0, 0x00, 0xFF, 0x00 }, // Forest
    { 1, 0xFF, 0x3C, 0x00 }, // Fire
    { 2, 0x00, 0x64, 0xFF }, // Water
    { 4, 0xC8, 0x32, 0xFF }, // Shadow
    { 3, 0xFF, 0x82, 0x00 }, // Spirit
};

uint8_t reward_rows[] = { 0, 1, 2, 4, 5, 6, 8, 7, 3 };

extern uint32_t CFG_DUNGEON_INFO_MQ_ENABLE;
extern uint32_t CFG_DUNGEON_INFO_MQ_NEED_MAP;
extern uint32_t CFG_DUNGEON_INFO_REWARD_ENABLE;
extern uint32_t CFG_DUNGEON_INFO_REWARD_NEED_COMPASS;
extern uint32_t CFG_DUNGEON_INFO_REWARD_NEED_ALTAR;
extern uint32_t CFG_DUNGEON_INFO_REWARD_SUMMARY_ENABLE;

extern int8_t CFG_DUNGEON_REWARDS[14];
extern char CFG_DUNGEON_REWARD_AREAS[9][0x17];

void draw_background(z64_disp_buf_t *db, int bg_left, int bg_top, int bg_width, int bg_height) {
    gDPSetCombineMode(db->p++, G_CC_PRIMITIVE, G_CC_PRIMITIVE);
    gDPSetPrimColor(db->p++, 0, 0, 0x00, 0x00, 0x00, 0xD0);
    gSPTextureRectangle(db->p++,
            bg_left<<2, bg_top<<2,
            (bg_left + bg_width)<<2, (bg_top + bg_height)<<2,
            0,
            0, 0,
            1<<10, 1<<10);

    gDPPipeSync(db->p++);
    gDPSetCombineMode(db->p++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);
}

void draw_dungeon_info(z64_disp_buf_t *db) {
    pad_t pad_held = z64_ctxt.input[0].raw.pad;
    int draw = CAN_DRAW_DUNGEON_INFO && !CAN_DRAW_TRADE_DPAD && (pad_held.dl || pad_held.dr || pad_held.dd || pad_held.a);
    if (!draw) {
        return;
    }

    db->p = db->buf;

    // Call setup display list
    gSPDisplayList(db->p++, &setup_db);

    if (pad_held.a) {
        uint16_t altar_flags = z64_file.inf_table[27];
        int show_medals = CFG_DUNGEON_INFO_REWARD_ENABLE && (!CFG_DUNGEON_INFO_REWARD_NEED_ALTAR || (altar_flags & 1)) && CFG_DUNGEON_INFO_REWARD_SUMMARY_ENABLE;
        int show_stones = CFG_DUNGEON_INFO_REWARD_ENABLE && (!CFG_DUNGEON_INFO_REWARD_NEED_ALTAR || (altar_flags & 2)) && CFG_DUNGEON_INFO_REWARD_SUMMARY_ENABLE;
        int show_keys = 1;
        int show_map_compass = 1;
        int show_skulls = 1;
        int show_mq = CFG_DUNGEON_INFO_MQ_ENABLE;

        // Set up dimensions

        int icon_size = 12;
        int font_width = 6;
        int font_height = 11;
        int padding = 1;
        int rows = 13;
        int mq_width = show_mq ?
            ((6 * font_width) + padding) :
            0;
        int bg_width =
            (6 * icon_size) +
            (11 * font_width) +
            (8 * padding) +
            mq_width;
        int bg_height = (rows * icon_size) + ((rows + 1) * padding);
        int bg_left = (Z64_SCREEN_WIDTH - bg_width) / 2;
        int bg_top = (Z64_SCREEN_HEIGHT - bg_height) / 2;

        int left = bg_left + padding;
        int start_top = bg_top + padding;

        // Draw background

        gDPSetCombineMode(db->p++, G_CC_PRIMITIVE, G_CC_PRIMITIVE);
        gDPSetPrimColor(db->p++, 0, 0, 0x00, 0x00, 0x00, 0xD0);
        gSPTextureRectangle(db->p++,
                bg_left<<2, bg_top<<2,
                (bg_left + bg_width)<<2, (bg_top + bg_height)<<2,
                0,
                0, 0,
                1<<10, 1<<10);
        
        gDPPipeSync(db->p++);
        gDPSetCombineMode(db->p++, G_CC_MODULATEIA_PRIM, G_CC_MODULATEIA_PRIM);

        // Draw medals

        if (show_medals) {
            sprite_load(db, &medals_sprite, 0, medals_sprite.tile_count);

            for (int i = 0; i < dungeon_count; i++) {
                dungeon_entry_t *d = &(dungeons[i]);
                if (CFG_DUNGEON_INFO_REWARD_NEED_COMPASS && !z64_file.dungeon_items[d->index].compass) {
                    continue;
                }
                int reward = CFG_DUNGEON_REWARDS[d->index];
                if (reward < 3) continue;
                reward -= 3;

                // Medal color index was changed to hint order,
                // moving Light from the end to the beginning.
                // Spirit/Shadow are also swapped.
                int reward_index;
                if (reward < 3) {
                    reward_index = reward + 1;
                } else if (reward == 3) {
                    reward_index = 5;
                } else if (reward == 4) {
                    reward_index = 4;
                } else if (reward == 5) {
                    reward_index = 0;
                }
                medal_t *c = &(medals[reward_index]);
                gDPSetPrimColor(db->p++, 0, 0, c->r, c->g, c->b, 0xFF);

                int top = start_top + ((icon_size + padding) * i);
                sprite_draw(db, &medals_sprite, reward,
                        left, top, icon_size, icon_size);
            }
        }

        gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xFF);

        // Draw stones

        if (show_stones) {
            sprite_load(db, &stones_sprite, 0, stones_sprite.tile_count);

            for (int i = 0; i < dungeon_count; i++) {
                dungeon_entry_t *d = &(dungeons[i]);
                if (CFG_DUNGEON_INFO_REWARD_NEED_COMPASS && !z64_file.dungeon_items[d->index].compass) {
                    continue;
                }
                int reward = CFG_DUNGEON_REWARDS[d->index];
                if (reward < 0 || reward >= 3) continue;

                int top = start_top + ((icon_size + padding) * i);
                sprite_draw(db, &stones_sprite, reward,
                        left, top, icon_size, icon_size);
            }
        }

        left += icon_size + padding;

        // Draw dungeon names

        for (int i = 0; i < dungeon_count; i++) {
            dungeon_entry_t *d = &(dungeons[i]);
            int top = start_top + ((icon_size + padding) * i) + 1;
            text_print_size(d->name, left, top, font_width);
        }
        text_flush_size(db, font_width, font_height, 0, 0);

        left += (8 * font_width) + padding;

        // Draw keys
        
        if (show_keys) {
            // Draw small key counts

            sprite_load(db, &quest_items_sprite, 17, 1);

            for (int i = 0; i < dungeon_count; i++) {
                dungeon_entry_t *d = &(dungeons[i]);
                if (!d->has_keys) continue;

                int8_t current_keys = z64_file.dungeon_keys[d->index];
                if (current_keys < 0) current_keys = 0;
                if (current_keys > 9) current_keys = 9;

                int8_t total_keys = z64_file.scene_flags[d->index].unk_00_ >> 0x10;
                if (total_keys < 0) total_keys = 0;
                if (total_keys > 9) total_keys = 9;

                char count[5] = "O(O)";
                if (current_keys > 0) count[0] = current_keys + '0';
                if (total_keys > 0) count[2] = total_keys + '0';
                int top = start_top + ((icon_size + padding) * i) + 1;
                text_print_size(count, left, top, font_width);
            }
            text_flush_size(db, font_width, font_height, 0, 0);

            left += (4 * font_width) + padding;

            // Draw boss keys

            sprite_load(db, &quest_items_sprite, 14, 1);

            for (int i = 0; i < dungeon_count; i++) {
                dungeon_entry_t *d = &(dungeons[i]);
                // Replace index 13 (Ganon's Castle) with 10 (Ganon's Tower)
                int index = d->index == 13 ? 10 : d->index;

                if (d->has_boss_key && z64_file.dungeon_items[index].boss_key) {
                    int top = start_top + ((icon_size + padding) * i);
                    sprite_draw(db, &quest_items_sprite, 0,
                            left, top, icon_size, icon_size);
                }
            }

            // Draw gerudo card

            sprite_load(db, &quest_items_sprite, 10, 1);

            for (int i = 0; i < dungeon_count; i++) {
                dungeon_entry_t *d = &(dungeons[i]);
                if (d->has_card && z64_file.gerudos_card) {
                    int top = start_top + ((icon_size + padding) * i);
                    sprite_draw(db, &quest_items_sprite, 0,
                            left, top, icon_size, icon_size);
                }
            }

            left += icon_size + padding;
        }

        // Draw maps and compasses

        if (show_map_compass) {
            // Draw maps

            sprite_load(db, &quest_items_sprite, 16, 1);

            for (int i = 0; i < dungeon_count; i++) {
                dungeon_entry_t *d = &(dungeons[i]);
                if (d->has_map && z64_file.dungeon_items[d->index].map) {
                    int top = start_top + ((icon_size + padding) * i);
                    sprite_draw(db, &quest_items_sprite, 0,
                            left, top, icon_size, icon_size);
                }
            }

            left += icon_size + padding;

            // Draw compasses

            sprite_load(db, &quest_items_sprite, 15, 1);

            for (int i = 0; i < dungeon_count; i++) {
                dungeon_entry_t *d = &(dungeons[i]);
                if (d->has_map && z64_file.dungeon_items[d->index].compass) {
                    int top = start_top + ((icon_size + padding) * i);
                    sprite_draw(db, &quest_items_sprite, 0,
                            left, top, icon_size, icon_size);
                }
            }

            left += icon_size + padding;
        }

        if (show_skulls) {
            // Draw skulltula icon

            sprite_load(db, &quest_items_sprite, 11, 1);

            for (int i = 0; i < dungeon_count; i++) {
                dungeon_entry_t *d = &(dungeons[i]);
                if (d->skulltulas && z64_file.gs_flags[d->index ^ 0x03] == d->skulltulas) {
                    int top = start_top + ((icon_size + padding) * i);
                    sprite_draw(db, &quest_items_sprite, 0,
                            left, top, icon_size, icon_size);
                }
            }

            left += icon_size + padding;
        }

        // Draw master quest dungeons

        if (show_mq) {
            for (int i = 0; i < dungeon_count; i++) {
                dungeon_entry_t *d = &(dungeons[i]);
                if (CFG_DUNGEON_INFO_MQ_NEED_MAP && d->has_map &&
                        !z64_file.dungeon_items[d->index].map) {
                    continue;
                }
                char *str = CFG_DUNGEON_IS_MQ[d->index] ? "MQ" : "Normal";
                int top = start_top + ((icon_size + padding) * i) + 1;
                text_print_size(str, left, top, font_width);
            }

            left += icon_size + padding;
        }
        text_flush_size(db, font_width, font_height, 0, 0);

        // Finish

    } else if (pad_held.dd) {
        uint16_t altar_flags = z64_file.inf_table[27];
        int show_medals = CFG_DUNGEON_INFO_REWARD_ENABLE && (!CFG_DUNGEON_INFO_REWARD_NEED_ALTAR || (altar_flags & 1));
        int show_stones = CFG_DUNGEON_INFO_REWARD_ENABLE && (!CFG_DUNGEON_INFO_REWARD_NEED_ALTAR || (altar_flags & 2));

        // Set up dimensions

        int icon_size = 16;
        int padding = 1;
        int rows = 9;
        int bg_width =
            (1 * icon_size) +
            (0x16 * font_sprite.tile_w) +
            (3 * padding);
        int bg_height = (rows * icon_size) + ((rows + 1) * padding);
        int bg_left = (Z64_SCREEN_WIDTH - bg_width) / 2;
        int bg_top = (Z64_SCREEN_HEIGHT - bg_height) / 2;

        int left = bg_left + padding;
        int start_top = bg_top + padding;

        draw_background(db, bg_left, bg_top, bg_width, bg_height);

        // Draw medals

        sprite_load(db, &medals_sprite, 0, medals_sprite.tile_count);

        for (int i = 3; i < 9; i++) {
            medal_t *medal = &(medals[i - 3]);
            gDPSetPrimColor(db->p++, 0, 0, medal->r, medal->g, medal->b, 0xFF);

            int top = start_top + ((icon_size + padding) * i);
            sprite_draw(db, &medals_sprite, medal->idx,
                    left, top, icon_size, icon_size);
        }

        gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xFF);

        // Draw stones

        sprite_load(db, &stones_sprite, 0, stones_sprite.tile_count);

        for (int i = 0; i < 3; i++) {
            int top = start_top + ((icon_size + padding) * i);
            sprite_draw(db, &stones_sprite, i,
                    left, top, icon_size, icon_size);
        }

        left += icon_size + padding;

        // Draw dungeon names

        for (int i = 0; i < 9; i++) {
            if (i < 3 ? show_stones : show_medals) {
                uint8_t reward = reward_rows[i];
                bool display_area = true;
                switch (CFG_DUNGEON_INFO_REWARD_NEED_COMPASS) {
                    case 1:
                        for (int j = 0; j < 8; j++) {
                            uint8_t dungeon_idx = dungeons[j].index;
                            if (CFG_DUNGEON_REWARDS[dungeon_idx] == reward) {
                                if (!z64_file.dungeon_items[dungeon_idx].compass) {
                                    display_area = false;
                                }
                                break;
                            }
                        }
                        break;
                    case 2:
                        if (i != 3) { // always display Light Medallion
                            dungeon_entry_t *d = &(dungeons[i - (i < 3 ? 0 : 1)]); // vanilla location of the reward
                            display_area = z64_file.dungeon_items[d->index].compass;
                        }
                        break;
                }
                if (!display_area) {
                    continue;
                }
                int top = start_top + ((icon_size + padding) * i) + 1;
                text_print(CFG_DUNGEON_REWARD_AREAS[i], left, top);
            }
        }

        left += (0x16 * font_sprite.tile_w) + padding;
    } else if (pad_held.dr) {
        int show_keys = 1;

        // Set up dimensions

        int icon_size = 16;
        int padding = 1;
        int rows = 9;
        int bg_width =
            (1 * icon_size) +
            (12 * font_sprite.tile_w) +
            (4 * padding);
        int bg_height = (rows * icon_size) + ((rows + 1) * padding);
        int bg_left = (Z64_SCREEN_WIDTH - bg_width) / 2;
        int bg_top = (Z64_SCREEN_HEIGHT - bg_height) / 2;

        int left = bg_left + padding;
        int start_top = bg_top + padding;

        draw_background(db, bg_left, bg_top, bg_width, bg_height);
        gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xFF);

        // Draw dungeon names

        for (int i = 0; i < 9; i++) {
            dungeon_entry_t *d = &(dungeons[i + (i > 5 ? 4 : 3)]); // skip Deku/DC/Jabu/Ice
            int top = start_top + ((icon_size + padding) * i) + 1;
            text_print(d->name, left, top);
        }

        left += (8 * font_sprite.tile_w) + padding;

        // Draw keys

        if (show_keys) {
            // Draw small key counts

            sprite_load(db, &quest_items_sprite, 17, 1);

            for (int i = 0; i < 9; i++) {
                dungeon_entry_t *d = &(dungeons[i + (i > 5 ? 4 : 3)]); // skip Deku/DC/Jabu/Ice
                if (!d->has_keys) continue;

                int8_t current_keys = z64_file.dungeon_keys[d->index];
                if (current_keys < 0) current_keys = 0;
                if (current_keys > 9) current_keys = 9;

                int8_t total_keys = z64_file.scene_flags[d->index].unk_00_ >> 0x10;
                if (total_keys < 0) total_keys = 0;
                if (total_keys > 9) total_keys = 9;

                char count[5] = "O(O)";
                if (current_keys > 0) count[0] = current_keys + '0';
                if (total_keys > 0) count[2] = total_keys + '0';
                int top = start_top + ((icon_size + padding) * i) + 1;
                text_print(count, left, top);
            }

            left += (4 * font_sprite.tile_w) + padding;

            // Draw boss keys

            sprite_load(db, &quest_items_sprite, 14, 1);

            for (int i = 0; i < 9; i++) {
                dungeon_entry_t *d = &(dungeons[i + (i > 5 ? 4 : 3)]); // skip Deku/DC/Jabu/Ice
                // Replace index 13 (Ganon's Castle) with 10 (Ganon's Tower)
                int index = d->index == 13 ? 10 : d->index;

                if (d->has_boss_key && z64_file.dungeon_items[index].boss_key) {
                    int top = start_top + ((icon_size + padding) * i);
                    sprite_draw(db, &quest_items_sprite, 0,
                            left, top, icon_size, icon_size);
                }
            }

            // Draw gerudo card

            sprite_load(db, &quest_items_sprite, 10, 1);

            for (int i = 0; i < 9; i++) {
                dungeon_entry_t *d = &(dungeons[i + (i > 5 ? 4 : 3)]); // skip Deku/DC/Jabu/Ice
                if (d->has_card && z64_file.gerudos_card) {
                    int top = start_top + ((icon_size + padding) * i);
                    sprite_draw(db, &quest_items_sprite, 0,
                            left, top, icon_size, icon_size);
                }
            }

            left += icon_size + padding;
        }
    } else { // pad_held.dl
        int show_map_compass = 1;
        int show_skulls = 1;
        int show_mq = CFG_DUNGEON_INFO_MQ_ENABLE;

        // Set up dimensions

        int icon_size = 16;
        int padding = 1;
        int rows = 12;
        int mq_width = show_mq ?
            ((6 * font_sprite.tile_w) + padding) :
            0;
        int bg_width =
            (3 * icon_size) +
            (8 * font_sprite.tile_w) +
            (8 * padding) +
            mq_width;
        int bg_height = (rows * icon_size) + ((rows + 1) * padding);
        int bg_left = (Z64_SCREEN_WIDTH - bg_width) / 2;
        int bg_top = (Z64_SCREEN_HEIGHT - bg_height) / 2;

        int left = bg_left + padding;
        int start_top = bg_top + padding;

        draw_background(db, bg_left, bg_top, bg_width, bg_height);
        gDPSetPrimColor(db->p++, 0, 0, 0xFF, 0xFF, 0xFF, 0xFF);

        // Draw dungeon names

        for (int i = 0; i < 12; i++) {
            dungeon_entry_t *d = &(dungeons[i + (i > 9 ? 1 : 0)]); // skip Hideout
            int top = start_top + ((icon_size + padding) * i) + 1;
            text_print(d->name, left, top);
        }

        left += (8 * font_sprite.tile_w) + padding;

        // Draw maps and compasses

        if (show_map_compass) {
            // Draw maps

            sprite_load(db, &quest_items_sprite, 16, 1);

            for (int i = 0; i < 12; i++) {
                dungeon_entry_t *d = &(dungeons[i + (i > 9 ? 1 : 0)]); // skip Hideout
                if (d->has_map && z64_file.dungeon_items[d->index].map) {
                    int top = start_top + ((icon_size + padding) * i);
                    sprite_draw(db, &quest_items_sprite, 0,
                            left, top, icon_size, icon_size);
                }
            }

            left += icon_size + padding;

            // Draw compasses

            sprite_load(db, &quest_items_sprite, 15, 1);

            for (int i = 0; i < 12; i++) {
                dungeon_entry_t *d = &(dungeons[i + (i > 9 ? 1 : 0)]); // skip Hideout
                if (d->has_map && z64_file.dungeon_items[d->index].compass) {
                    int top = start_top + ((icon_size + padding) * i);
                    sprite_draw(db, &quest_items_sprite, 0,
                            left, top, icon_size, icon_size);
                }
            }

            left += icon_size + padding;
        }

        if (show_skulls) {
            // Draw skulltula icon

            sprite_load(db, &quest_items_sprite, 11, 1);

            for (int i = 0; i < 12; i++) {
                dungeon_entry_t *d = &(dungeons[i + (i > 9 ? 1 : 0)]); // skip Hideout
                if (d->skulltulas && z64_file.gs_flags[d->index ^ 0x03] == d->skulltulas) {
                    int top = start_top + ((icon_size + padding) * i);
                    sprite_draw(db, &quest_items_sprite, 0,
                            left, top, icon_size, icon_size);
                }
            }

            left += icon_size + padding;
        }

        // Draw master quest dungeons

        if (show_mq) {
            for (int i = 0; i < 12; i++) {
                dungeon_entry_t *d = &(dungeons[i + (i > 9 ? 1 : 0)]); // skip Hideout
                if (CFG_DUNGEON_INFO_MQ_NEED_MAP && d->has_map &&
                        !z64_file.dungeon_items[d->index].map) {
                    continue;
                }
                char *str = CFG_DUNGEON_IS_MQ[d->index] ? "MQ" : "Normal";
                int top = start_top + ((icon_size + padding) * i) + 1;
                text_print(str, left, top);
            }

            left += icon_size + padding;
        }
    }

    // Finish

    text_flush(db);

    gDPFullSync(db->p++);
    gSPEndDisplayList(db->p++);
}
