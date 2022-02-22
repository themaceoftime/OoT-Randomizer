import os
import random
from enum import IntEnum

def get_model_choices_adult():
    names = ["Default"]
    if os.path.exists('data/Models/adult'):
        for file in os.listdir('data/Models/adult'):
            names.append(file.split('.')[0])
    if len(names) > 2:
        # If more than 2 non-default model choices, add random option
        names.insert(1, "Random")
    return names


def get_model_choices_child():
    names = ["Default"]
    if os.path.exists('data/Models/child'):
        for file in os.listdir('data/Models/child'):
            names.append(file.split('.')[0])
    if len(names) > 2:
        # If more than 2 non-default model choices, add random option
        names.insert(1, "Random")
    return names


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


def patch_model_adult(rom, settings, log):
    model = settings.model_adult + ".zobj"
    if settings.model_adult == "Random": 
        model = random.choice([x for x in os.listdir('data/Models/adult')])
    log.model = model.split('.')[0]
    writer = ModelDataWriter(rom)

    # Write adult Link pointer data
    writer.GoTo(0xE6718)
    writer.SetAdvance(8)
    writer.WriteModelData(Offsets.ADULT_LINK_LUT_DL_RFIST)
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
    writer.WriteModelData(0x00000000)
    writer.WriteModelData(0xC3B43333) # -360.4

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
    writer.WriteModelData(0x06005380) # Hierarchy pointer

    # Write zobj to adult object
    file = open('data/Models/adult/' + model, "rb")
    byte = file.read(1)
    offset = 0
    while byte:
        rom.write_byte(0x00F86000 + offset, byte[0])
        offset += 1
        byte = file.read(1)


def patch_model_child(rom, settings, log):
    model = settings.model_child + ".zobj"
    if settings.model_child == "Random": 
        model = random.choice([x for x in os.listdir('data/Models/child')])
    log.model = model.split('.')[0]
    writer = ModelDataWriter(rom)

    # Write child Link pointer data
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
    writer.WriteModelData(0x44178000) # 606.0
    writer.WriteModelData(0x436C0000) # 236.0

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
    writer.WriteModelData(0x060053A8) # Hierarchy pointer

    # Write zobj to child object
    file = open('data/Models/child/' + model, "rb")
    byte = file.read(1)
    offset = 0
    while byte:
        rom.write_byte(0x00FBE000 + offset, byte[0])
        offset += 1
        byte = file.read(1)


class Offsets(IntEnum):
    ADULT_LINK_LUT_DL_WAIST = 0x06005090
    ADULT_LINK_LUT_DL_RTHIGH = 0x06005098
    ADULT_LINK_LUT_DL_RSHIN = 0x060050A0
    ADULT_LINK_LUT_DL_RFOOT = 0x060050A8
    ADULT_LINK_LUT_DL_LTHIGH = 0x060050B0
    ADULT_LINK_LUT_DL_LSHIN = 0x060050B8
    ADULT_LINK_LUT_DL_LFOOT = 0x060050C0
    ADULT_LINK_LUT_DL_HEAD = 0x060050C8
    ADULT_LINK_LUT_DL_HAT = 0x060050D0
    ADULT_LINK_LUT_DL_COLLAR = 0x060050D8
    ADULT_LINK_LUT_DL_LSHOULDER = 0x060050E0
    ADULT_LINK_LUT_DL_LFOREARM = 0x060050E8
    ADULT_LINK_LUT_DL_RSHOULDER = 0x060050F0
    ADULT_LINK_LUT_DL_RFOREARM = 0x060050F8
    ADULT_LINK_LUT_DL_TORSO = 0x06005100
    ADULT_LINK_LUT_DL_LHAND = 0x06005108
    ADULT_LINK_LUT_DL_LFIST = 0x06005110
    ADULT_LINK_LUT_DL_LHAND_BOTTLE = 0x06005118
    ADULT_LINK_LUT_DL_RHAND = 0x06005120
    ADULT_LINK_LUT_DL_RFIST = 0x06005128
    ADULT_LINK_LUT_DL_SWORD_SHEATH = 0x06005130
    ADULT_LINK_LUT_DL_SWORD_HILT = 0x06005138
    ADULT_LINK_LUT_DL_SWORD_BLADE = 0x06005140
    ADULT_LINK_LUT_DL_LONGSWORD_HILT = 0x06005148
    ADULT_LINK_LUT_DL_LONGSWORD_BLADE = 0x06005150
    ADULT_LINK_LUT_DL_LONGSWORD_BROKEN = 0x06005158
    ADULT_LINK_LUT_DL_SHIELD_HYLIAN = 0x06005160
    ADULT_LINK_LUT_DL_SHIELD_MIRROR = 0x06005168
    ADULT_LINK_LUT_DL_HAMMER = 0x06005170
    ADULT_LINK_LUT_DL_BOTTLE = 0x06005178
    ADULT_LINK_LUT_DL_BOW = 0x06005180
    ADULT_LINK_LUT_DL_OCARINA_TIME = 0x06005188
    ADULT_LINK_LUT_DL_HOOKSHOT = 0x06005190
    ADULT_LINK_LUT_DL_UPGRADE_LFOREARM = 0x06005198
    ADULT_LINK_LUT_DL_UPGRADE_LHAND = 0x060051A0
    ADULT_LINK_LUT_DL_UPGRADE_LFIST = 0x506001A8
    ADULT_LINK_LUT_DL_UPGRADE_RFOREARM = 0x060051B0
    ADULT_LINK_LUT_DL_UPGRADE_RHAND = 0x060051B8
    ADULT_LINK_LUT_DL_UPGRADE_RFIST = 0x060051C0
    ADULT_LINK_LUT_DL_BOOT_LIRON = 0x060051C8
    ADULT_LINK_LUT_DL_BOOT_RIRON = 0x060051D0
    ADULT_LINK_LUT_DL_BOOT_LHOVER = 0x060051D8
    ADULT_LINK_LUT_DL_BOOT_RHOVER = 0x060051E0
    ADULT_LINK_LUT_DL_FPS_LFOREARM = 0x060051E8
    ADULT_LINK_LUT_DL_FPS_LHAND = 0x060051F0
    ADULT_LINK_LUT_DL_FPS_RFOREARM = 0x060051F8
    ADULT_LINK_LUT_DL_FPS_RHAND = 0x06005200
    ADULT_LINK_LUT_DL_FPS_HOOKSHOT = 0x06005208
    ADULT_LINK_LUT_DL_HOOKSHOT_CHAIN = 0x06005210
    ADULT_LINK_LUT_DL_HOOKSHOT_HOOK = 0x06005218
    ADULT_LINK_LUT_DL_HOOKSHOT_AIM = 0x06005220
    ADULT_LINK_LUT_DL_BOW_STRING = 0x06005228
    ADULT_LINK_LUT_DL_BLADEBREAK = 0x06005230
    ADULT_LINK_LUT_DL_SWORD_SHEATHED = 0x06005238
    ADULT_LINK_LUT_DL_SHIELD_HYLIAN_BACK = 0x06005258
    ADULT_LINK_LUT_DL_SHIELD_MIRROR_BACK = 0x06005268
    ADULT_LINK_LUT_DL_SWORD_SHIELD_HYLIAN = 0x06005278
    ADULT_LINK_LUT_DL_SWORD_SHIELD_MIRROR = 0x06005288
    ADULT_LINK_LUT_DL_SHEATH0_HYLIAN = 0x06005298
    ADULT_LINK_LUT_DL_SHEATH0_MIRROR = 0x060052A8
    ADULT_LINK_LUT_DL_LFIST_SWORD = 0x060052B8
    ADULT_LINK_LUT_DL_LFIST_LONGSWORD = 0x060052D0
    ADULT_LINK_LUT_DL_LFIST_LONGSWORD_BROKEN = 0x060052E8
    ADULT_LINK_LUT_DL_LFIST_HAMMER = 0x06005300
    ADULT_LINK_LUT_DL_RFIST_SHIELD_HYLIAN = 0x06005310
    ADULT_LINK_LUT_DL_RFIST_SHIELD_MIRROR = 0x06005320
    ADULT_LINK_LUT_DL_RFIST_BOW = 0x06005330
    ADULT_LINK_LUT_DL_RFIST_HOOKSHOT = 0x06005340
    ADULT_LINK_LUT_DL_RHAND_OCARINA_TIME = 0x06005350
    ADULT_LINK_LUT_DL_FPS_RHAND_BOW = 0x06005360
    ADULT_LINK_LUT_DL_FPS_LHAND_HOOKSHOT = 0x06005370

    CHILD_LINK_LUT_DL_SHIELD_DEKU = 0x060050D0
    CHILD_LINK_LUT_DL_WAIST = 0x060050D8
    CHILD_LINK_LUT_DL_RTHIGH = 0x060050E0
    CHILD_LINK_LUT_DL_RSHIN = 0x060050E8
    CHILD_LINK_LUT_DL_RFOOT = 0x060050F0
    CHILD_LINK_LUT_DL_LTHIGH = 0x060050F8
    CHILD_LINK_LUT_DL_LSHIN = 0x06005100
    CHILD_LINK_LUT_DL_LFOOT = 0x06005108
    CHILD_LINK_LUT_DL_HEAD = 0x06005110
    CHILD_LINK_LUT_DL_HAT = 0x06005118
    CHILD_LINK_LUT_DL_COLLAR = 0x06005120
    CHILD_LINK_LUT_DL_LSHOULDER = 0x06005128
    CHILD_LINK_LUT_DL_LFOREARM = 0x06005130
    CHILD_LINK_LUT_DL_RSHOULDER = 0x06005138
    CHILD_LINK_LUT_DL_RFOREARM = 0x06005140
    CHILD_LINK_LUT_DL_TORSO = 0x06005148
    CHILD_LINK_LUT_DL_LHAND = 0x06005150
    CHILD_LINK_LUT_DL_LFIST = 0x06005158
    CHILD_LINK_LUT_DL_LHAND_BOTTLE = 0x06005160
    CHILD_LINK_LUT_DL_RHAND = 0x06005168
    CHILD_LINK_LUT_DL_RFIST = 0x06005170
    CHILD_LINK_LUT_DL_SWORD_SHEATH = 0x06005178
    CHILD_LINK_LUT_DL_SWORD_HILT = 0x06005180
    CHILD_LINK_LUT_DL_SWORD_BLADE = 0x06005188
    CHILD_LINK_LUT_DL_SLINGSHOT = 0x06005190
    CHILD_LINK_LUT_DL_OCARINA_FAIRY = 0x06005198
    CHILD_LINK_LUT_DL_OCARINA_TIME = 0x060051A0
    CHILD_LINK_LUT_DL_DEKU_STICK = 0x060051A8
    CHILD_LINK_LUT_DL_BOOMERANG = 0x060051B0
    CHILD_LINK_LUT_DL_SHIELD_HYLIAN_BACK = 0x060051B8
    CHILD_LINK_LUT_DL_BOTTLE = 0x060051C0
    CHILD_LINK_LUT_DL_MASTER_SWORD = 0x060051C8
    CHILD_LINK_LUT_DL_GORON_BRACELET = 0x060051D0
    CHILD_LINK_LUT_DL_FPS_RIGHT_ARM = 0x060051D8
    CHILD_LINK_LUT_DL_SLINGSHOT_STRING = 0x060051E0
    CHILD_LINK_LUT_DL_MASK_BUNNY = 0x060051E8
    CHILD_LINK_LUT_DL_MASK_GERUDO = 0x060051F0
    CHILD_LINK_LUT_DL_MASK_GORON = 0x060051F8
    CHILD_LINK_LUT_DL_MASK_KEATON = 0x06005200
    CHILD_LINK_LUT_DL_MASK_SPOOKY = 0x06005208
    CHILD_LINK_LUT_DL_MASK_TRUTH = 0x06005210
    CHILD_LINK_LUT_DL_MASK_ZORA = 0x06005218
    CHILD_LINK_LUT_DL_MASK_SKULL = 0x06005220
    CHILD_LINK_DL_SWORD_SHEATHED = 0x06005228
    CHILD_LINK_LUT_DL_SWORD_SHEATHED = 0x06005248
    CHILD_LINK_DL_SHIELD_DEKU_ODD = 0x06005250
    CHILD_LINK_LUT_DL_SHIELD_DEKU_ODD = 0x06005260
    CHILD_LINK_DL_SHIELD_DEKU_BACK = 0x06005268
    CHILD_LINK_LUT_DL_SHIELD_DEKU_BACK = 0x06005278
    CHILD_LINK_DL_SWORD_SHIELD_HYLIAN = 0x06005280
    CHILD_LINK_LUT_DL_SWORD_SHIELD_HYLIAN = 0x06005290
    CHILD_LINK_DL_SWORD_SHIELD_DEKU = 0x06005298
    CHILD_LINK_LUT_DL_SWORD_SHIELD_DEKU = 0x060052A8
    CHILD_LINK_DL_SHEATH0_HYLIAN = 0x060052B0
    CHILD_LINK_LUT_DL_SHEATH0_HYLIAN = 0x060052C0
    CHILD_LINK_DL_SHEATH0_DEKU = 0x060052C8
    CHILD_LINK_LUT_DL_SHEATH0_DEKU = 0x060052D8
    CHILD_LINK_DL_LFIST_SWORD = 0x060052E0
    CHILD_LINK_LUT_DL_LFIST_SWORD = 0x060052F8
    CHILD_LINK_DL_LHAND_PEDESTALSWORD = 0x06005300
    CHILD_LINK_LUT_DL_LHAND_PEDESTALSWORD = 0x06005310
    CHILD_LINK_DL_LFIST_BOOMERANG = 0x06005318
    CHILD_LINK_LUT_DL_LFIST_BOOMERANG = 0x06005328
    CHILD_LINK_DL_RFIST_SHIELD_DEKU = 0x06005330
    CHILD_LINK_LUT_DL_RFIST_SHIELD_DEKU = 0x06005340
    CHILD_LINK_DL_RFIST_SLINGSHOT = 0x06005348
    CHILD_LINK_LUT_DL_RFIST_SLINGSHOT = 0x06005358
    CHILD_LINK_DL_RHAND_OCARINA_FAIRY = 0x06005360
    CHILD_LINK_LUT_DL_RHAND_OCARINA_FAIRY = 0x06005370
    CHILD_LINK_DL_RHAND_OCARINA_TIME = 0x06005378
    CHILD_LINK_LUT_DL_RHAND_OCARINA_TIME = 0x06005388
    CHILD_LINK_DL_FPS_RARM_SLINGSHOT = 0x06005390
