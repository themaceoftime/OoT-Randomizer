#include "z64.h"
#include "item_table.h"
#include "get_items.h"
#include "textures.h"
#include "obj_comb.h"

#define GAMEPLAY_FIELD_KEEP_BEEHIVE_TEXTURE (uint8_t*)0x05008900

// Hack beehives to drop a collectible w / an extended flag, based on the grotto param ?
void obj_comb_drop_collectible(z64_actor_t *actor, int16_t params)
{
    // Check if we're in a grotto
    uint8_t flag = actor->rot_init.z;
    if (z64_game.scene_index == 0x3E)
    {
        // We're in a grotto so offset by 2x grotto id. The Rz flags for the grottos need to be set to 0/1 beforehand.
        flag = (2 * (z64_file.grotto_id & 0x1F)) + flag;
        // and add 0x60
        flag += 0x60;
    }

    if (params >= 0)
    {
        // set up params for Item_DropCollectible
        params |= ((flag & 0x3F) << 8) + (flag & 0xC0);
        z64_Item_DropCollectible2(&z64_game, &actor->pos_2, params);
    }
}

override_t get_beehive_override(z64_actor_t *actor, z64_game_t *game)
{
    uint8_t flag = actor->rot_init.z;
    if (z64_game.scene_index == 0x3E)
    {
        // We're in a grotto so offset by 2x grotto id. The Rz flags for the grottos need to be set to 0/1 beforehand.
        flag = (2 * (z64_file.grotto_id & 0x1F)) + flag;
        // and add 0x60
        flag += 0x60;
    }

    EnItem00 dummy;
    dummy.collectibleFlag = flag;
    dummy.actor.actor_id = 0x15;
    dummy.actor.dropFlag = 1;
    dummy.actor.variable = 0;
    if (!should_override_collectible(&dummy))
    {
        return (override_t){0};
    }

    return lookup_override((z64_actor_t *)&dummy, game->scene_index, 0);
}


void ObjComb_Update(z64_actor_t* thisx, z64_game_t* game)
{
    ObjComb* this = (ObjComb*)thisx;
    if(this->actor.dropFlag > 0)
        this->actor.dropFlag --;
    this->unk_1B2 += 0x2EE0;
    this->actionFunc(this, game);
    this->actor.rot_2.x = z64_Math_SinS(this->unk_1B2) * this->unk_1B0 + this->actor.rot_1.x;

    override_t override = get_beehive_override(thisx, game);

    if(override.key.all != 0)
    {

        uint16_t item_id = resolve_upgrades(override.value.item_id);
        item_row_t *row = get_item_row(override.value.looks_like_item_id);
        if (row == NULL) {
            row = get_item_row(override.value.item_id);
        }
        if (row->chest_type > 0)
        {
            if(this->unk_1B0 == 0 && this->actor.dropFlag == 0)
            {
                this->unk_1B0 = 0x0800;
                this->actor.dropFlag = 0x40;
            }
        }
    }
}

void ObjComb_Draw_Hack(z64_actor_t* this, z64_game_t* game)
{
    uint8_t *texture = GAMEPLAY_FIELD_KEEP_BEEHIVE_TEXTURE;

    override_t override = get_beehive_override(this, game);

    if(override.key.all != 0)
    {

        uint16_t item_id = resolve_upgrades(override.value.item_id);
        item_row_t *row = get_item_row(override.value.looks_like_item_id);
        if (row == NULL) {
            row = get_item_row(override.value.item_id);
        }
        if (row->chest_type == GILDED_CHEST)
        {
            texture = get_texture(TEXTURE_ID_BEEHIVE_GOLD);
        }
        if (row->chest_type == GOLD_CHEST)
        {
            texture = get_texture(TEXTURE_ID_BEEHIVE_BOSSKEY);
        }
    }

    z64_gfx_t *gfx = game->common.gfx;
    gfx->poly_opa.d -= 2;
    gDPSetTextureImage(gfx->poly_opa.d, G_IM_FMT_RGBA, G_IM_SIZ_16b, 1, texture);
    gSPEndDisplayList(gfx->poly_opa.d + 1);
    gMoveWd(gfx->poly_opa.p++, G_MW_SEGMENT, 9 * sizeof(int), gfx->poly_opa.d);
}