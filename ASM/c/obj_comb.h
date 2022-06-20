#include "z64.h"

struct ObjComb;

typedef void (*ObjCombActionFunc)(struct ObjComb*, z64_game_t*);

typedef struct ObjComb {
    /* 0x0000 */ z64_actor_t actor;
    /* 0x013C */ ObjCombActionFunc actionFunc;
    /* 0x0140 */ uint8_t unk_00[0x60];
    /* 0x01A0 */ uint16_t unk_1B0;
    /* 0x01A2 */ uint16_t unk_1B2;
} ObjComb; // size = 0x01A4