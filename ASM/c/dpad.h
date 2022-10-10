#ifndef DPAD_H
#define DPAD_H

#include "dungeon_info.h"
#include "z64.h"

#define BLOCK_DPAD (0x00000001 | \
                    0x00000002 | \
                    0x00000080 | \
                    0x00000400 | \
                    0x10000000 | \
                    0x20000000)

#define BLOCK_ITEMS (0x00800000 | \
                     0x00000800 | \
                     0x00200000 | \
                     0x08000000)

extern uint16_t CFG_ADULT_TRADE_SHUFFLE;
extern uint16_t CFG_CHILD_TRADE_SHUFFLE;

#define CAN_DRAW_TRADE_DPAD (z64_game.pause_ctxt.state == 6 && \
                            z64_game.pause_ctxt.screen_idx == 0 && \
                            (!z64_game.pause_ctxt.changing || z64_game.pause_ctxt.changing == 3) && \
                            ((z64_game.pause_ctxt.item_cursor == Z64_SLOT_ADULT_TRADE && CFG_ADULT_TRADE_SHUFFLE) || \
                            (z64_game.pause_ctxt.item_cursor == Z64_SLOT_CHILD_TRADE && CFG_CHILD_TRADE_SHUFFLE)))

#define CAN_USE_TRADE_DPAD  (CAN_DRAW_TRADE_DPAD && z64_game.pause_ctxt.changing != 3)

#define DISPLAY_DPAD        ((((z64_file.iron_boots || z64_file.hover_boots) && z64_file.link_age == 0) || \
                            ((z64_file.items[Z64_SLOT_CHILD_TRADE] >= Z64_ITEM_WEIRD_EGG && z64_file.items[Z64_SLOT_CHILD_TRADE] <= Z64_ITEM_MASK_OF_TRUTH) && z64_file.link_age == 1) || \
                            z64_file.items[Z64_SLOT_OCARINA] == Z64_ITEM_FAIRY_OCARINA || z64_file.items[Z64_SLOT_OCARINA] == Z64_ITEM_OCARINA_OF_TIME) && \
                            !CAN_DRAW_TRADE_DPAD)

#define CAN_USE_DPAD        (((z64_link.state_flags_1 & BLOCK_DPAD) == 0) && \
                            ((uint32_t)z64_ctxt.state_dtor==z64_state_ovl_tab[3].vram_dtor) && \
                            (z64_file.game_mode == 0) && \
                            ((z64_event_state_1 & 0x20) == 0) && \
                            !CAN_DRAW_DUNGEON_INFO)

#define CAN_USE_OCARINA     (z64_game.pause_ctxt.state == 0 && (z64_file.items[Z64_SLOT_OCARINA] == Z64_ITEM_FAIRY_OCARINA || z64_file.items[Z64_SLOT_OCARINA] == Z64_ITEM_OCARINA_OF_TIME) && !z64_game.restriction_flags.ocarina && ((z64_link.state_flags_1 & BLOCK_ITEMS) == 0))
#define CAN_USE_CHILD_TRADE (z64_game.pause_ctxt.state == 0 && z64_file.items[Z64_SLOT_CHILD_TRADE] >= Z64_ITEM_WEIRD_EGG && z64_file.items[Z64_SLOT_CHILD_TRADE] <= Z64_ITEM_MASK_OF_TRUTH && !z64_game.restriction_flags.trade_items && ((z64_link.state_flags_1 & BLOCK_ITEMS) == 0))

void handle_dpad();
void draw_dpad();

#endif
