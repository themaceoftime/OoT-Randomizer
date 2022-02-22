import os
import random
import struct
from enum import IntEnum
from N64Patch import apply_patch_file

def get_model_choices():
    names = ["None", "Random"]
    if os.path.exists('data/Models'):
        for file in os.listdir('data/Models'):
            names.append(file.split('.')[0])
    return names


def patch_model_zpf(rom, settings, log):
    model = settings.model + ".zpf"
    if settings.model == "Random": 
        model = random.choice([x for x in os.listdir('data/Models')])
    apply_patch_file(rom, 'data/Models/' + model)


class ModelDataWriter:

    def __init__(self, rom):
        self.rom = rom
        self.offset = 0
        self.advance = 4
        self.SetBase('Code')
    
    def SetBase(self, base):
        if base == 'Code':
            self.base = 0x00A87000 # start of code
        elif base == 'Player':
            self.base = 0x00BCDB70
        elif base == 'Hook':
            self.base = 0x00CAD2C0
        elif base == 'Shield':
            self.base = 0x00DB1F40
        elif base == 'Stick':
            self.base = 0x00EAD0F0

    def GoTo(self, dest):
        self.offset = dest

    def SetAdvance(self, adv):
        self.advance = adv

    def GetAddress(self):
        return self.base + self.offset

    def WriteModelData(self, data):
        self.rom.write_bytes(self.GetAddress(), data.to_bytes(4, 'big'))
        self.offset += self.advance

    def WriteModelData16(self, data):
        self.rom.write_bytes(self.GetAddress(), data.to_bytes(2, 'big'))
        self.offset += 2

    def WriteModelDataFloat(self, data):
        bytes = bytearray(struct.pack("f", data))
        self.rom.write_bytes(self.GetAddress(), bytes)
        self.offset += 4

    def WriteModelDataHi(self, data):
        bytes = data.to_bytes(4, 'big')
        for i in range(2):
            self.rom.write_byte(self.GetAddress(), bytes[i])
            self.offset += 1

    def WriteModelDataLo(self, data):
        bytes = data.to_bytes(4, 'big')
        for i in range(2, 4):
            self.rom.write_byte(self.GetAddress(), bytes[i])
            self.offset += 1


def patch_model(rom, settings, log):
    model = settings.model + ".zobj"
    if settings.model == "Random": 
        model = random.choice([x for x in os.listdir('data/Models')])
    log.model = model.split('.')[0]
    writer = ModelDataWriter(rom)

    # Write adult Link data
    writer.GoTo(0xE6718)
    writer.SetAdvance(8)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RFIST)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SHIELD_HYLIAN)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SHIELD_HYLIAN)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RFIST_SHIELD_HYLIAN)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RFIST_SHIELD_HYLIAN)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RFIST_SHIELD_MIRROR)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RFIST_SHIELD_MIRROR)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SWORD_SHEATHED)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SWORD_SHEATHED)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SHIELD_HYLIAN)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SHIELD_HYLIAN)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SWORD_SHIELD_HYLIAN)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SWORD_SHIELD_HYLIAN)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SWORD_SHIELD_MIRROR)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SWORD_SHIELD_MIRROR)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SWORD_SHEATH)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SWORD_SHEATH)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SHIELD_HYLIAN)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SHIELD_HYLIAN)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SHEATH0_HYLIAN)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SHEATH0_HYLIAN)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SHEATH0_MIRROR)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SHEATH0_MIRROR)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_LFIST_LONGSWORD)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_LFIST_LONGSWORD)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_LFIST_LONGSWORD_BROKEN)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_LFIST_LONGSWORD_BROKEN)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_LHAND)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_LHAND)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_LFIST)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_LFIST)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SHIELD_HYLIAN)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SHIELD_HYLIAN)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_LFIST_SWORD)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_LFIST_SWORD)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RHAND)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RHAND)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RFIST)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RFIST)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RFIST_BOW)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RFIST_BOW)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SWORD_SHEATHED)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SWORD_SHEATHED)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SWORD_SHEATH)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SWORD_SHEATH)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_WAIST)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_WAIST)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RFIST_BOW)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RFIST_BOW)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RHAND_OCARINA_TIME)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RHAND_OCARINA_TIME)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RHAND_OCARINA_TIME)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RHAND_OCARINA_TIME)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RFIST_HOOKSHOT)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RFIST_HOOKSHOT)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_LFIST_HAMMER)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_LFIST_HAMMER)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SHIELD_HYLIAN)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_SHIELD_HYLIAN)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_LHAND_BOTTLE)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_LHAND_BOTTLE)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_FPS_LFOREARM)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_FPS_LHAND)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RSHOULDER)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_FPS_RFOREARM)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_FPS_RHAND_BOW)

    writer.GoTo(0xE6A4C)
    writer.SetAdvance(4)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_BOOT_LIRON)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_BOOT_RIRON)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_BOOT_LHOVER)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_BOOT_RHOVER)

    writer.GoTo(0xE6B28)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_BOTTLE)

    writer.GoTo(0xE6B64)
    writer.SetAdvance(4)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_BOW_STRING)
    writer.WriteModelDataFloat(0.0)
    writer.WriteModelDataFloat(-360.4)

    writer.GoTo(0x69112)
    writer.WriteModelDataHi(Offsets.ADULT_LINK_LUT_DL_UPGRADE_LFOREARM)
    writer.GoTo(0x69116)
    writer.WriteModelDataLo(Offsets.ADULT_LINK_LUT_DL_UPGRADE_LFOREARM)
    writer.GoTo(0x6912E)
    writer.WriteModelDataHi(Offsets.ADULT_LINK_LUT_DL_UPGRADE_RFOREARM)
    writer.GoTo(0x69132)
    writer.WriteModelDataLo(Offsets.ADULT_LINK_LUT_DL_UPGRADE_RFOREARM)
    writer.GoTo(0x6914E)
    writer.WriteModelDataHi(Offsets.ADULT_LINK_LUT_DL_UPGRADE_LFIST)
    writer.GoTo(0x69162)
    writer.WriteModelDataLo(Offsets.ADULT_LINK_LUT_DL_UPGRADE_LFIST)
    writer.GoTo(0x69166)
    writer.WriteModelDataHi(Offsets.ADULT_LINK_LUT_DL_UPGRADE_LHAND)
    writer.GoTo(0x69172)
    writer.WriteModelDataLo(Offsets.ADULT_LINK_LUT_DL_UPGRADE_LHAND)
    writer.GoTo(0x6919E)
    writer.WriteModelDataHi(Offsets.ADULT_LINK_LUT_DL_UPGRADE_RFIST)
    writer.GoTo(0x691A2)
    writer.WriteModelDataLo(Offsets.ADULT_LINK_LUT_DL_UPGRADE_RFIST)
    writer.GoTo(0x691AE)
    writer.WriteModelDataHi(Offsets.ADULT_LINK_LUT_DL_UPGRADE_RHAND)
    writer.GoTo(0x691B2)
    writer.WriteModelDataLo(Offsets.ADULT_LINK_LUT_DL_UPGRADE_RHAND)
    writer.GoTo(0x69DEA)
    writer.WriteModelDataHi(Offsets.ADULT_LINK_LUT_DL_FPS_LHAND_HOOKSHOT)
    writer.GoTo(0x69DEE)
    writer.WriteModelDataLo(Offsets.ADULT_LINK_LUT_DL_FPS_LHAND_HOOKSHOT)
    writer.GoTo(0x6A666)
    writer.WriteModelDataHi(Offsets.ADULT_LINK_LUT_DL_HOOKSHOT_AIM)
    writer.GoTo(0x6A66A)
    writer.WriteModelDataLo(Offsets.ADULT_LINK_LUT_DL_HOOKSHOT_AIM)

    writer.SetBase('Hook')
    writer.GoTo(0xA72)
    writer.WriteModelDataHi(Offsets.ADULT_LINK_LUT_DL_HOOKSHOT_HOOK)
    writer.GoTo(0xA76)
    writer.WriteModelDataLo(Offsets.ADULT_LINK_LUT_DL_HOOKSHOT_HOOK)
    writer.GoTo(0xB66)
    writer.WriteModelDataHi(Offsets.ADULT_LINK_LUT_DL_HOOKSHOT_CHAIN)
    writer.GoTo(0xB6A)
    writer.WriteModelDataLo(Offsets.ADULT_LINK_LUT_DL_HOOKSHOT_CHAIN)
    writer.GoTo(0xBA8)
    writer.WriteModelData16(0x0014)

    writer.SetBase('Stick')
    writer.GoTo(0x32C)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_BLADEBREAK)
    writer.GoTo(0x328)
    writer.WriteModelData16(0x0014)

    writer.SetBase('Code')
    writer.GoTo(0xE65A0)
    writer.WriteModelData(0x06005830)

    # Write child Link data
    writer.GoTo(0xE671C)
    writer.SetAdvance(8)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RFIST)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RFIST)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RFIST_SHIELD_DEKU)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RFIST_SHIELD_DEKU)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SHIELD_DEKU)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SHIELD_DEKU)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SHIELD_DEKU)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SHIELD_DEKU)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SWORD_SHEATHED)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SWORD_SHEATHED)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SWORD_SHIELD_DEKU)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SWORD_SHIELD_DEKU)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SWORD_SHIELD_HYLIAN)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SWORD_SHIELD_HYLIAN)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SHIELD_DEKU)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SHIELD_DEKU)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SHIELD_DEKU_BACK)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SHIELD_DEKU_BACK)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SWORD_SHEATH)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SWORD_SHEATH)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SHEATH0_DEKU)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SHEATH0_DEKU)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SHEATH0_HYLIAN)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SHEATH0_HYLIAN)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SHIELD_DEKU)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SHIELD_DEKU)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SHIELD_DEKU_BACK)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SHIELD_DEKU_BACK)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LHAND_PEDESTALSWORD)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LHAND_PEDESTALSWORD)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LHAND_PEDESTALSWORD)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LHAND_PEDESTALSWORD)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LHAND)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LHAND)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LFIST)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LFIST)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LFIST_SWORD)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LFIST_SWORD)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LFIST_SWORD)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LFIST_SWORD)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RHAND)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RHAND)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RFIST)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RFIST)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RFIST_SLINGSHOT)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RFIST_SLINGSHOT)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SWORD_SHEATHED)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SWORD_SHEATHED)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SWORD_SHEATH)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SWORD_SHEATH)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_WAIST)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_WAIST)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RFIST_SLINGSHOT)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RFIST_SLINGSHOT)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RHAND_OCARINA_FAIRY)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RHAND_OCARINA_FAIRY)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RHAND_OCARINA_TIME)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RHAND_OCARINA_TIME)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RFIST)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RFIST)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LFIST)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LFIST)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LFIST_BOOMERANG)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LFIST_BOOMERANG)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LHAND_BOTTLE)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_LHAND_BOTTLE)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_RSHOULDER)
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_FPS_RIGHT_ARM)

    writer.GoTo(0xE6B2C)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_BOTTLE)

    writer.GoTo(0xE6B74)
    writer.SetAdvance(4)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SLINGSHOT_STRING)
    writer.WriteModelData(0x44178000)
    writer.WriteModelData(0x436C0000)

    writer.GoTo(0x6922E)
    writer.WriteModelDataHi(Offsets.CHILD_LINK_LUT_DL_GORON_BRACELET)
    writer.GoTo(0x69232)
    writer.WriteModelDataLo(Offsets.CHILD_LINK_LUT_DL_GORON_BRACELET)
    writer.GoTo(0x6A80E)
    writer.WriteModelDataHi(Offsets.CHILD_LINK_LUT_DL_DEKU_STICK)
    writer.GoTo(0x6A812)
    writer.WriteModelDataLo(Offsets.CHILD_LINK_LUT_DL_DEKU_STICK)

    writer.SetBase('Stick')
    writer.GoTo(0x334)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_DEKU_STICK)
    writer.GoTo(0x330)
    writer.WriteModelData16(0x0015)

    writer.SetBase('Shield')
    writer.GoTo(0x7EE)
    writer.WriteModelDataHi(Offsets.CHILD_LINK_LUT_DL_SHIELD_DEKU_ODD)
    writer.GoTo(0x7F2)
    writer.WriteModelDataLo(Offsets.CHILD_LINK_LUT_DL_SHIELD_DEKU_ODD)

    writer.SetBase('Player')
    writer.GoTo(0x2253C)
    writer.SetAdvance(4)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_MASK_KEATON)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_MASK_SKULL)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_MASK_SPOOKY)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_MASK_BUNNY)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_MASK_GORON)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_MASK_ZORA)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_MASK_GERUDO)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_MASK_TRUTH)

    writer.SetBase('Code')
    writer.GoTo(0xE65A4)
    writer.WriteModelData(0x06005830)

    # Write zobj to adult object (will separate child and adult later)
    file = open('data/Models/' + model, "rb")
    byte = file.read(1)
    offset = 0
    while byte:
        rom.write_byte(0x00F86000 + offset, byte[0])
        offset += 1
        byte = file.read(1)
    # child is 0x00FBE000


class Offsets(IntEnum):
    ADULT_LINK_LUT_DL_WAIST = 0x5090
    ADULT_LINK_LUT_DL_RTHIGH = 0x5098
    ADULT_LINK_LUT_DL_RSHIN = 0x50A0
    ADULT_LINK_LUT_DL_RFOOT = 0x50A8
    ADULT_LINK_LUT_DL_LTHIGH = 0x50B0
    ADULT_LINK_LUT_DL_LSHIN = 0x50B8
    ADULT_LINK_LUT_DL_LFOOT = 0x50C0
    ADULT_LINK_LUT_DL_HEAD = 0x50C8
    ADULT_LINK_LUT_DL_HAT = 0x50D0
    ADULT_LINK_LUT_DL_COLLAR = 0x50D8
    ADULT_LINK_LUT_DL_LSHOULDER = 0x50E0
    ADULT_LINK_LUT_DL_LFOREARM = 0x50E8
    ADULT_LINK_LUT_DL_RSHOULDER = 0x50F0
    ADULT_LINK_LUT_DL_RFOREARM = 0x50F8
    ADULT_LINK_LUT_DL_TORSO = 0x5100
    ADULT_LINK_LUT_DL_LHAND = 0x5108
    ADULT_LINK_LUT_DL_LFIST = 0x5110
    ADULT_LINK_LUT_DL_LHAND_BOTTLE = 0x5118
    ADULT_LINK_LUT_DL_RHAND = 0x5120
    ADULT_LINK_LUT_DL_RFIST = 0x5128
    ADULT_LINK_LUT_DL_SWORD_SHEATH = 0x5130
    ADULT_LINK_LUT_DL_SWORD_HILT = 0x5138
    ADULT_LINK_LUT_DL_SWORD_BLADE = 0x5140
    ADULT_LINK_LUT_DL_LONGSWORD_HILT = 0x5148
    ADULT_LINK_LUT_DL_LONGSWORD_BLADE = 0x5150
    ADULT_LINK_LUT_DL_LONGSWORD_BROKEN = 0x5158
    ADULT_LINK_LUT_DL_SHIELD_HYLIAN = 0x5160
    ADULT_LINK_LUT_DL_SHIELD_MIRROR = 0x5168
    ADULT_LINK_LUT_DL_HAMMER = 0x5170
    ADULT_LINK_LUT_DL_BOTTLE = 0x5178
    ADULT_LINK_LUT_DL_BOW = 0x5180
    ADULT_LINK_LUT_DL_OCARINA_TIME = 0x5188
    ADULT_LINK_LUT_DL_HOOKSHOT = 0x5190
    ADULT_LINK_LUT_DL_UPGRADE_LFOREARM = 0x5198
    ADULT_LINK_LUT_DL_UPGRADE_LHAND = 0x51A0
    ADULT_LINK_LUT_DL_UPGRADE_LFIST = 0x51A8
    ADULT_LINK_LUT_DL_UPGRADE_RFOREARM = 0x51B0
    ADULT_LINK_LUT_DL_UPGRADE_RHAND = 0x51B8
    ADULT_LINK_LUT_DL_UPGRADE_RFIST = 0x51C0
    ADULT_LINK_LUT_DL_BOOT_LIRON = 0x51C8
    ADULT_LINK_LUT_DL_BOOT_RIRON = 0x51D0
    ADULT_LINK_LUT_DL_BOOT_LHOVER = 0x51D8
    ADULT_LINK_LUT_DL_BOOT_RHOVER = 0x51E0
    ADULT_LINK_LUT_DL_FPS_LFOREARM = 0x51E8
    ADULT_LINK_LUT_DL_FPS_LHAND = 0x51F0
    ADULT_LINK_LUT_DL_FPS_RFOREARM = 0x51F8
    ADULT_LINK_LUT_DL_FPS_RHAND = 0x5200
    ADULT_LINK_LUT_DL_FPS_HOOKSHOT = 0x5208
    ADULT_LINK_LUT_DL_HOOKSHOT_CHAIN = 0x5210
    ADULT_LINK_LUT_DL_HOOKSHOT_HOOK = 0x5218
    ADULT_LINK_LUT_DL_HOOKSHOT_AIM = 0x5220
    ADULT_LINK_LUT_DL_BOW_STRING = 0x5228
    ADULT_LINK_LUT_DL_BLADEBREAK = 0x5230
    ADULT_LINK_LUT_DL_SWORD_SHEATHED = 0x5238
    ADULT_LINK_LUT_DL_SHIELD_HYLIAN_BACK = 0x5258
    ADULT_LINK_LUT_DL_SHIELD_MIRROR_BACK = 0x5268
    ADULT_LINK_LUT_DL_SWORD_SHIELD_HYLIAN = 0x5278
    ADULT_LINK_LUT_DL_SWORD_SHIELD_MIRROR = 0x5288
    ADULT_LINK_LUT_DL_SHEATH0_HYLIAN = 0x5298
    ADULT_LINK_LUT_DL_SHEATH0_MIRROR = 0x52A8
    ADULT_LINK_LUT_DL_LFIST_SWORD = 0x52B8
    ADULT_LINK_LUT_DL_LFIST_LONGSWORD = 0x52D0
    ADULT_LINK_LUT_DL_LFIST_LONGSWORD_BROKEN = 0x52E8
    ADULT_LINK_LUT_DL_LFIST_HAMMER = 0x5300
    ADULT_LINK_LUT_DL_RFIST_SHIELD_HYLIAN = 0x5310
    ADULT_LINK_LUT_DL_RFIST_SHIELD_MIRROR = 0x5320
    ADULT_LINK_LUT_DL_RFIST_BOW = 0x5330
    ADULT_LINK_LUT_DL_RFIST_HOOKSHOT = 0x5340
    ADULT_LINK_LUT_DL_RHAND_OCARINA_TIME = 0x5350
    ADULT_LINK_LUT_DL_FPS_RHAND_BOW = 0x5360
    ADULT_LINK_LUT_DL_FPS_LHAND_HOOKSHOT = 0x5370

    CHILD_LINK_LUT_DL_SHIELD_DEKU = 0x50D0
    CHILD_LINK_LUT_DL_WAIST = 0x50D8
    CHILD_LINK_LUT_DL_RTHIGH = 0x50E0
    CHILD_LINK_LUT_DL_RSHIN = 0x50E8
    CHILD_LINK_LUT_DL_RFOOT = 0x50F0
    CHILD_LINK_LUT_DL_LTHIGH = 0x50F8
    CHILD_LINK_LUT_DL_LSHIN = 0x5100
    CHILD_LINK_LUT_DL_LFOOT = 0x5108
    CHILD_LINK_LUT_DL_HEAD = 0x5110
    CHILD_LINK_LUT_DL_HAT = 0x5118
    CHILD_LINK_LUT_DL_COLLAR = 0x5120
    CHILD_LINK_LUT_DL_LSHOULDER = 0x5128
    CHILD_LINK_LUT_DL_LFOREARM = 0x5130
    CHILD_LINK_LUT_DL_RSHOULDER = 0x5138
    CHILD_LINK_LUT_DL_RFOREARM = 0x5140
    CHILD_LINK_LUT_DL_TORSO = 0x5148
    CHILD_LINK_LUT_DL_LHAND = 0x5150
    CHILD_LINK_LUT_DL_LFIST = 0x5158
    CHILD_LINK_LUT_DL_LHAND_BOTTLE = 0x5160
    CHILD_LINK_LUT_DL_RHAND = 0x5168
    CHILD_LINK_LUT_DL_RFIST = 0x5170
    CHILD_LINK_LUT_DL_SWORD_SHEATH = 0x5178
    CHILD_LINK_LUT_DL_SWORD_HILT = 0x5180
    CHILD_LINK_LUT_DL_SWORD_BLADE = 0x5188
    CHILD_LINK_LUT_DL_SLINGSHOT = 0x5190
    CHILD_LINK_LUT_DL_OCARINA_FAIRY = 0x5198
    CHILD_LINK_LUT_DL_OCARINA_TIME = 0x51A0
    CHILD_LINK_LUT_DL_DEKU_STICK = 0x51A8
    CHILD_LINK_LUT_DL_BOOMERANG = 0x51B0
    CHILD_LINK_LUT_DL_SHIELD_HYLIAN_BACK = 0x51B8
    CHILD_LINK_LUT_DL_BOTTLE = 0x51C0
    CHILD_LINK_LUT_DL_MASTER_SWORD = 0x51C8
    CHILD_LINK_LUT_DL_GORON_BRACELET = 0x51D0
    CHILD_LINK_LUT_DL_FPS_RIGHT_ARM = 0x51D8
    CHILD_LINK_LUT_DL_SLINGSHOT_STRING = 0x51E0
    CHILD_LINK_LUT_DL_MASK_BUNNY = 0x51E8
    CHILD_LINK_LUT_DL_MASK_GERUDO = 0x51F0
    CHILD_LINK_LUT_DL_MASK_GORON = 0x51F8
    CHILD_LINK_LUT_DL_MASK_KEATON = 0x5200
    CHILD_LINK_LUT_DL_MASK_SPOOKY = 0x5208
    CHILD_LINK_LUT_DL_MASK_TRUTH = 0x5210
    CHILD_LINK_LUT_DL_MASK_ZORA = 0x5218
    CHILD_LINK_LUT_DL_MASK_SKULL = 0x5220
    CHILD_LINK_DL_SWORD_SHEATHED = 0x5228
    CHILD_LINK_LUT_DL_SWORD_SHEATHED = 0x5248
    CHILD_LINK_DL_SHIELD_DEKU_ODD = 0x5250
    CHILD_LINK_LUT_DL_SHIELD_DEKU_ODD = 0x5260
    CHILD_LINK_DL_SHIELD_DEKU_BACK = 0x5268
    CHILD_LINK_LUT_DL_SHIELD_DEKU_BACK = 0x5278
    CHILD_LINK_DL_SWORD_SHIELD_HYLIAN = 0x5280
    CHILD_LINK_LUT_DL_SWORD_SHIELD_HYLIAN = 0x5290
    CHILD_LINK_DL_SWORD_SHIELD_DEKU = 0x5298
    CHILD_LINK_LUT_DL_SWORD_SHIELD_DEKU = 0x52A8
    CHILD_LINK_DL_SHEATH0_HYLIAN = 0x52B0
    CHILD_LINK_LUT_DL_SHEATH0_HYLIAN = 0x52C0
    CHILD_LINK_DL_SHEATH0_DEKU = 0x52C8
    CHILD_LINK_LUT_DL_SHEATH0_DEKU = 0x52D8
    CHILD_LINK_DL_LFIST_SWORD = 0x52E0
    CHILD_LINK_LUT_DL_LFIST_SWORD = 0x52F8
    CHILD_LINK_DL_LHAND_PEDESTALSWORD = 0x5300
    CHILD_LINK_LUT_DL_LHAND_PEDESTALSWORD = 0x5310
    CHILD_LINK_DL_LFIST_BOOMERANG = 0x5318
    CHILD_LINK_LUT_DL_LFIST_BOOMERANG = 0x5328
    CHILD_LINK_DL_RFIST_SHIELD_DEKU = 0x5330
    CHILD_LINK_LUT_DL_RFIST_SHIELD_DEKU = 0x5340
    CHILD_LINK_DL_RFIST_SLINGSHOT = 0x5348
    CHILD_LINK_LUT_DL_RFIST_SLINGSHOT = 0x5358
    CHILD_LINK_DL_RHAND_OCARINA_FAIRY = 0x5360
    CHILD_LINK_LUT_DL_RHAND_OCARINA_FAIRY = 0x5370
    CHILD_LINK_DL_RHAND_OCARINA_TIME = 0x5378
    CHILD_LINK_LUT_DL_RHAND_OCARINA_TIME = 0x5388
    CHILD_LINK_DL_FPS_RARM_SLINGSHOT = 0x5390
