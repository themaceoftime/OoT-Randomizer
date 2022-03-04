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

# Either return the starting index of the footer (when start == 0)
# or if the element exists in the footer (start > 0)
def findfooter(bytes, string, start=0):
    stringbytes = string.encode()
    stringindex = 0
    for i in range(start, len(bytes)):
        # Byte matches next byte in string
        if bytes[i] == stringbytes[stringindex]:
            stringindex += 1
            # All bytes have been found, so a match
            if stringindex == len(stringbytes):
                # If start is 0 then looking for the footer, return the index
                if start == 0:
                    return i + 1
                # Else we just want to know if it exists
                else:
                    return True
        # Match has been broken, reset to start of string
        else:
            stringindex = 0
    return False

def unwrap(zobj, address):
    # An entry in the LUT will look something like 0xDE 01 0000 06014050
    # Only the last 3 bytes should be necessary.
    data = int.from_bytes(zobj[address+5:address+8], 'big')
    # If the data here points to another entry in the LUT, keep searching until
    # an address outside the table is found.
    while 0x5000 <= data and data <= 0x5800:
        address = data
        data = int.from_bytes(zobj[address+5:address+8], 'big')
    return address


def WriteDL(dl, index, data):
    bytes = data.to_bytes(4, 'big')
    for i in range(4):
        dl[index + i] = bytes[i]


def Optimize(rom, missing, rebase, linkstart, linksize, pieces):
    # Get vanilla "zobj" of Link's model
    vanillaData = []
    for i in range(linksize):
        vanillaData.append(rom.buffer[linkstart + i])
    segment = 0x06
    vertices = {}
    matrices = {}
    textures = {}
    displayLists = []
    # For each missing piece, grab data from its vanilla display list
    for item in missing:
        offset = pieces[item][1]
        i = offset
        displayList = []
        # Crawl displaylist bytecode and handle each command
        while i < len(vanillaData):
            op = vanillaData[i]
            seg = vanillaData[i+4]
            lo = int.from_bytes(vanillaData[i+4:i+8], 'big')
            if op == 0xDF: # End of list
                break
            # Shouldn't have to deal with DE (branch to new display list)
            elif op == 0x01 and seg == segment: # Vertex data
                vtxStart = lo & 0x00FFFFFF
                vtxLen = int.from_bytes(vanillaData[i+1:i+3], 'big')
                if vtxStart not in vertices or len(vertices[vtxStart]) < vtxLen:
                    vertices[vtxStart] = vanillaData[vtxStart:vtxStart+vtxLen]
            elif op == 0xDA and seg == segment: # Push matrix
                mtxStart = lo & 0x00FFFFFF
                # error if start + 0x40 > vanillaData len
                if mtxStart not in matrices:
                    matrices[mtxStart] = vanillaData[mtxStart:mtxStart+0x40] # Matrices always 0x40 long
            elif op == 0xFD and seg == segment: # Texture
                # Comment from original code: "Don't ask me how this works"
                textureType = (vanillaData[i+1] >> 3) & 0x1F
                numTexelBits = 4 * (2 ** (textureType & 0x3))
                bytesPerTexel = int(numTexelBits / 8)
                texOffset = lo & 0x00FFFFFF
                isPalette = vanillaData[i+8] == 0xE8
                numTexels = -1
                returnStack = []
                j = i+8
                while j < len(vanillaData) and numTexels == -1:
                    opJ = vanillaData[j]
                    segJ = vanillaData[j+4]
                    loJ = int.from_bytes(vanillaData[j+4:j+8], 'big')
                    if opJ == 0xDF:
                        if len(returnStack) == 0:
                            numTexels = 0
                            break
                        else:
                            j = returnStack.pop()
                    elif opJ == 0xFD:
                        numTexels = 0
                        break
                    elif opJ == 0xDE:
                        if segJ == segment:
                            if vanillaData[j+1] == 0x0:
                                returnStack.push(j)
                            j = loJ & 0x00FFFFFF
                    elif opJ == 0xF0:
                        if isPalette:
                            numTexels = ((loJ & 0x00FFF000) >> 14) + 1
                        # Else error
                        break
                        # Also error if numTexels > 256
                    elif opJ == 0xF3:
                        if not isPalette:
                            numTexels = ((loJ & 0x00FFF000) >> 12) + 1
                        # Else error
                        break
                    j += 8
                # Error if numTexels == -1
                dataLen = bytesPerTexel * numTexels
                # Error if texOffset + dataLen > len(zobj)
                if texOffset not in textures or len(textures[texOffset]) < dataLen:
                    textures[texOffset] = vanillaData[texOffset:texOffset+dataLen]
            displayList.extend(vanillaData[i:i+8])
            i += 8
        displayLists.append((displayList, offset))
    # Create optimized zobj from data collected during crawl
    optimizedZobj = []
    # Textures
    oldTex2New = {}
    texLengths = {}
    for (offset, texture) in textures.items():
        newOffset = len(optimizedZobj)
        oldTex2New[offset] = newOffset
        texLengths[offset] = len(texture)
        optimizedZobj.extend(texture)
    # Vertices
    oldVer2New = {}
    vertLengths = {}
    for (offset, vertex) in vertices.items():
        newOffset = len(optimizedZobj)
        oldVer2New[offset] = newOffset
        vertLengths[offset] = len(vertex)
        optimizedZobj.extend(vertex)
    # Matrices
    oldMtx2New = {}
    mtxLengths = {}
    for (offset, matrix) in matrices.items():
        newOffset = len(optimizedZobj)
        oldMtx2New[offset] = newOffset
        mtxLengths[offset] = len(matrix)
        optimizedZobj.extend(matrix)
    # Display lists
    oldDL2New = {}
    for data in displayLists:
        dl = data[0]
        offset = data[1]
        oldDL2New[offset] = len(optimizedZobj)
        for i in range (0, len(dl), 8):
            op = dl[i]
            seg = dl[i+4]
            lo = int.from_bytes(dl[i+4:i+8], 'big')
            if seg == segment:
                if op == 0x01:
                    vertEntry = oldVer2New[lo & 0x00FFFFFF]
                    WriteDL(dl, i + 4, 0x06000000 + vertEntry + rebase)
                elif op == 0xDA:
                    mtxEntry = oldMtx2New[lo & 0x00FFFFFF]
                    WriteDL(dl, i + 4, 0x06000000 + mtxEntry + rebase)
                elif op == 0xFD:
                    texEntry = oldTex2New[lo & 0x00FFFFFF]
                    WriteDL(dl, i + 4, 0x06000000 + texEntry + rebase)
                elif op == 0xDE:
                    dlEntry = oldDL2New[lo & 0x00FFFFFF]
                    WriteDL(dl, i + 4, 0x06000000 + dlEntry + rebase)
        optimizedZobj.extend(dl)
    # Pad to nearest multiple of 16
    while len(optimizedZobj) % 0x10 != 0:
        optimizedZobj.append(0x00)
    # Now find the relation of items to new offsets
    DLOffsets = {}
    for item in missing:
        DLOffsets[item] = oldDL2New[pieces[item][1]]
    return (optimizedZobj, DLOffsets)


def LoadModel(rom, model, age):
    # age 0 = adult, 1 = child
    linkstart = ADULT_START
    linksize = ADULT_SIZE
    pieces = AdultPieces
    path = 'data/Models/adult/'
    if age == 1:
        linkstart = CHILD_START
        linksize = CHILD_SIZE
        pieces = ChildPieces
        path = 'data/Models/child/'
    # Read model data from file
    file = open(path + model, "rb")
    zobj = file.read()
    file.close()
    zobj = bytearray(zobj)
    # Find which pieces are missing from this model
    start = findfooter(zobj, "!PlayAsManifest0")
    missing = []
    for piece in pieces:
        if not findfooter(zobj, piece, start):
            missing.append(piece)
    #missing.append("Hookshot")
    if len(missing) > 0:
        # Optimize the missing pieces to make them work in the new zobj
        (optimizedZobj, DLOffsets) = Optimize(rom, missing, len(zobj), linkstart, linksize, pieces)
        startaddr = start - len("!PlayAsManifest0")
        # Write optimized zobj data to end of model zobj
        i = 0
        for byte in optimizedZobj:
            zobj.insert(startaddr + i, byte)
            i += 1
        # Now we have to update the lookup table for each item
        for item in missing:
            lut = pieces[item][0] - 0x06000000
            entry = unwrap(zobj, lut) + 5
            dladdress = DLOffsets[item] + len(zobj)
            dladdressbytes = dladdress.to_bytes(3, 'big')
            for byte in dladdressbytes:
                zobj[entry] = byte
                entry += 1
    # Write zobj to vanilla object (object_link_boy or object_link_child)
    rom.write_bytes(linkstart, zobj)

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
    writer.WriteModelData(0x00000000) # string anchor x: 0.0
    writer.WriteModelData(0xC3B43333) # string anchor y: -360.4

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

    LoadModel(rom, model, 0)


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
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_FPS_RARM_SLINGSHOT)

    writer.GoTo(0xE6B2C)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_BOTTLE)

    writer.GoTo(0xE6B74)
    writer.SetAdvance(4)
    writer.WriteModelData(Offsets.CHILD_LINK_LUT_DL_SLINGSHOT_STRING)
    writer.WriteModelData(0x44178000) # string anchor x: 606.0
    writer.WriteModelData(0x436C0000) # string anchor y: 236.0

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

    LoadModel(rom, model, 1)


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
    ADULT_LINK_LUT_DL_UPGRADE_LFIST = 0x060051A8
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
    CHILD_LINK_LUT_DL_FPS_RARM_SLINGSHOT = 0x060053A0

# Adult model pieces and their offsets
AdultPieces = {
    "Sheath": (Offsets.ADULT_LINK_LUT_DL_SWORD_SHEATH, 0x249D8),
    "FPS.Hookshot": (Offsets.ADULT_LINK_LUT_DL_FPS_HOOKSHOT, 0x24D70), # Same as non-fps hookshot, couldn't find an address for fps specifically
    "Hilt.2": (Offsets.ADULT_LINK_LUT_DL_SWORD_HILT, 0x21F78), # Same as master sword, need to have it stop when end of hilt reached
    "Blade.2": (Offsets.ADULT_LINK_LUT_DL_SWORD_BLADE, 0x21F78),  # Need to remove fist and hilt
    "Hookshot.Spike": (Offsets.ADULT_LINK_LUT_DL_HOOKSHOT_HOOK, 0x2B288),
    "Hookshot": (Offsets.ADULT_LINK_LUT_DL_HOOKSHOT, 0x24D70), # Need to remove fist
    "Fist.L": (Offsets.ADULT_LINK_LUT_DL_LFIST, 0x21CE8), # Length: 0x290
    "Fist.R": (Offsets.ADULT_LINK_LUT_DL_RFIST, 0x226E0), # Length: 0x290
    "FPS.Forearm.L": (Offsets.ADULT_LINK_LUT_DL_FPS_LFOREARM, 0x29FA0),
    "FPS.Forearm.R": (Offsets.ADULT_LINK_LUT_DL_FPS_RFOREARM, 0x29918),
    # Maybe need to reverse gauntler order, decomp just calls them plate 1-3
    "Gauntlet.Fist.L": (Offsets.ADULT_LINK_LUT_DL_UPGRADE_LFIST, 0x25218),
    "Gauntlet.Fist.R": (Offsets.ADULT_LINK_LUT_DL_UPGRADE_RFIST, 0x25598),
    "Gauntlet.Forearm.L": (Offsets.ADULT_LINK_LUT_DL_UPGRADE_LFOREARM, 0x252D8),
    "Gauntlet.Forearm.R": (Offsets.ADULT_LINK_LUT_DL_UPGRADE_RFOREARM, 0x25658),
    "Gauntlet.Hand.L": (Offsets.ADULT_LINK_LUT_DL_UPGRADE_LHAND, 0x25438),
    "Gauntlet.Hand.R": (Offsets.ADULT_LINK_LUT_DL_UPGRADE_RHAND, 0x257B8),
    "Bottle.Hand.L": (Offsets.ADULT_LINK_LUT_DL_LHAND_BOTTLE, 0x29600),
    "FPS.Hand.L": (Offsets.ADULT_LINK_LUT_DL_FPS_LHAND, 0x24B58), # Length: 0x220
    "FPS.Hand.R": (Offsets.ADULT_LINK_LUT_DL_FPS_RHAND, 0x29C20), # Length: 0x380
    "Bow.String": (Offsets.ADULT_LINK_LUT_DL_BOW_STRING, 0x2B108),
    "Bow": (Offsets.ADULT_LINK_LUT_DL_BOW, 0x22DA8), # Need to remove fist
    "Blade.3.Break": (Offsets.ADULT_LINK_LUT_DL_BLADEBREAK, 0x2BA38),
    "Blade.3": (Offsets.ADULT_LINK_LUT_DL_LONGSWORD_BLADE, 0x238C8), # Need to remove fist
    "Bottle": (Offsets.ADULT_LINK_LUT_DL_BOTTLE, 0x2AD58), 
    "Broken.Blade.3": (Offsets.ADULT_LINK_LUT_DL_LONGSWORD_BROKEN, 0x23D50), # Need to remove fist
    "Foot.2.L": (Offsets.ADULT_LINK_LUT_DL_BOOT_LIRON, 0x25918),
    "Foot.2.R": (Offsets.ADULT_LINK_LUT_DL_BOOT_RIRON, 0x25A60),
    "Foot.3.L": (Offsets.ADULT_LINK_LUT_DL_BOOT_LHOVER, 0x25BA8),
    "Foot.3.R": (Offsets.ADULT_LINK_LUT_DL_BOOT_RHOVER, 0x25DB0),
    "Hammer": (Offsets.ADULT_LINK_LUT_DL_HAMMER, 0x233E0), # Need to remove fist
    "Hookshot.Aiming.Reticule": (Offsets.ADULT_LINK_LUT_DL_HOOKSHOT_AIM, 0x2CB48),
    "Hookshot.Chain": (Offsets.ADULT_LINK_LUT_DL_HOOKSHOT_CHAIN, 0x2AFF0),
    "Ocarina.2": (Offsets.ADULT_LINK_LUT_DL_OCARINA_TIME, 0x24698), # Need to remove fist
    "Shield.2": (Offsets.ADULT_LINK_LUT_DL_SHIELD_HYLIAN, 0x22970), # Need to remove fist
    "Shield.3": (Offsets.ADULT_LINK_LUT_DL_SHIELD_MIRROR, 0x241C0), # Need to remove fist
    "Limb 1": (Offsets.ADULT_LINK_LUT_DL_WAIST, 0x35330),
    "Limb 3": (Offsets.ADULT_LINK_LUT_DL_RTHIGH, 0x35678),
    "Limb 4": (Offsets.ADULT_LINK_LUT_DL_RSHIN, 0x358B0),
    "Limb 5": (Offsets.ADULT_LINK_LUT_DL_RFOOT, 0x358B0),
    "Limb 6": (Offsets.ADULT_LINK_LUT_DL_LTHIGH, 0x35CB8),
    "Limb 7": (Offsets.ADULT_LINK_LUT_DL_LSHIN, 0x35EF0),
    "Limb 8": (Offsets.ADULT_LINK_LUT_DL_LFOOT, 0x361A0),
    "Limb 10": (Offsets.ADULT_LINK_LUT_DL_HEAD, 0x365E8),
    "Limb 11": (Offsets.ADULT_LINK_LUT_DL_HAT, 0x36D30),
    "Limb 12": (Offsets.ADULT_LINK_LUT_DL_COLLAR, 0x362F8),
    "Limb 13": (Offsets.ADULT_LINK_LUT_DL_LSHOULDER, 0x37210),
    "Limb 14": (Offsets.ADULT_LINK_LUT_DL_LFOREARM, 0x373D8),
    "Limb 15": (Offsets.ADULT_LINK_LUT_DL_LHAND, 0x21AA8),
    "Limb 16": (Offsets.ADULT_LINK_LUT_DL_RSHOULDER, 0x36E58),
    "Limb 17": (Offsets.ADULT_LINK_LUT_DL_RFOREARM, 0x37018),
    "Limb 18": (Offsets.ADULT_LINK_LUT_DL_RHAND, 0x22498),
    "Limb 20": (Offsets.ADULT_LINK_LUT_DL_TORSO, 0x363B8),
}

ChildPieces = {
    "Slingshot.String": (Offsets.CHILD_LINK_LUT_DL_SLINGSHOT_STRING, 0x221A8),
    "Sheath": (Offsets.CHILD_LINK_LUT_DL_SWORD_HILT, 0x15408),
    "Blade.2": (Offsets.ADULT_LINK_LUT_DL_SWORD_BLADE, 0x15540), # Presumably for pulling the sword animation
    "Blade.1": (Offsets.CHILD_LINK_LUT_DL_SWORD_BLADE, 0x13F38), # Need to remove fist and hilt
    "Boomerang": (Offsets.CHILD_LINK_LUT_DL_BOOMERANG, 0x14660), # Need to remove fist
    "Fist.L": (Offsets.CHILD_LINK_LUT_DL_LFIST, 0x13E18),
    "Fist.R": (Offsets.CHILD_LINK_LUT_DL_RFIST, 0x14320),
    "Hilt.1": (Offsets.CHILD_LINK_LUT_DL_SWORD_HILT, 0x13F38), # Same as kokiri sword, need to have it stop when end of hilt reached
    "Shield.1": (Offsets.CHILD_LINK_LUT_DL_SHIELD_DEKU, 0x14440), # Need to remove fist
    "Slingshot": (Offsets.CHILD_LINK_LUT_DL_SLINGSHOT, 0x15DF0), # Need to remove fist
    "Ocarina.1": (Offsets.CHILD_LINK_LUT_DL_OCARINA_FAIRY, 0x15BA8), # Need to remove fist
    "Bottle": (Offsets.CHILD_LINK_LUT_DL_BOTTLE, 0x18478),
    "Ocarina.2": (Offsets.CHILD_LINK_LUT_DL_OCARINA_TIME, 0x15958), # Need to remove fist
    "Bottle.Hand.L": (Offsets.CHILD_LINK_LUT_DL_LHAND_BOTTLE, 0x18478), # Just the bottle, couldn't find one with hand and bottle
    "GoronBracelet": (Offsets.CHILD_LINK_LUT_DL_GORON_BRACELET, 0x16118),
    "Mask.Skull": (Offsets.CHILD_LINK_LUT_DL_MASK_SKULL, 0x2AD40),
    "Mask.Spooky": (Offsets.CHILD_LINK_LUT_DL_MASK_SPOOKY, 0x2AF70),
    "Mask.Gerudo": (Offsets.CHILD_LINK_LUT_DL_MASK_GERUDO, 0x2B788),
    "Mask.Goron": (Offsets.CHILD_LINK_LUT_DL_MASK_GORON, 0x2B350),
    "Mask.Keaton": (Offsets.CHILD_LINK_LUT_DL_MASK_KEATON, 0x2B060),
    "Mask.Truth": (Offsets.CHILD_LINK_LUT_DL_MASK_TRUTH, 0x2B1F0),
    "Mask.Zora": (Offsets.CHILD_LINK_LUT_DL_MASK_ZORA, 0x2B580),
    "FPS.Forearm.R": (Offsets.CHILD_LINK_LUT_DL_FPS_RIGHT_ARM, 0x18048), # Need to remove slingshot?
    "Deku Stick": (Offsets.CHILD_LINK_LUT_DL_DEKU_STICK, 0x6CC0),
    "Shield.2": (Offsets.CHILD_LINK_LUT_DL_SHIELD_HYLIAN_BACK, 0x14B40), # Need to remove sheath
    "Limb 1": (Offsets.CHILD_LINK_LUT_DL_WAIST, 0x202A8),
    "Limb 3": (Offsets.CHILD_LINK_LUT_DL_RTHIGH, 0x204F0),
    "Limb 4": (Offsets.CHILD_LINK_LUT_DL_RSHIN, 0x206E8),
    "Limb 5": (Offsets.CHILD_LINK_LUT_DL_RFOOT, 0x20978),
    "Limb 6": (Offsets.CHILD_LINK_LUT_DL_LTHIGH, 0x20AD8),
    "Limb 7": (Offsets.CHILD_LINK_LUT_DL_LSHIN, 0x20CD0),
    "Limb 8": (Offsets.CHILD_LINK_LUT_DL_LFOOT, 0x20F60),
    "Limb 10": (Offsets.CHILD_LINK_LUT_DL_HEAD, 0x21360),
    "Limb 11": (Offsets.CHILD_LINK_LUT_DL_HAT, 0x219B0),
    "Limb 12": (Offsets.CHILD_LINK_LUT_DL_COLLAR, 0x210C0),
    "Limb 13": (Offsets.CHILD_LINK_LUT_DL_LSHOULDER, 0x21E18),
    "Limb 14": (Offsets.CHILD_LINK_LUT_DL_LFOREARM, 0x21FE8),
    "Limb 15": (Offsets.CHILD_LINK_LUT_DL_LHAND, 0x13CB0),
    "Limb 16": (Offsets.CHILD_LINK_LUT_DL_RSHOULDER, 0x21AE8),
    "Limb 17": (Offsets.CHILD_LINK_LUT_DL_RFOREARM, 0x21CB8),
    "Limb 18": (Offsets.CHILD_LINK_LUT_DL_RHAND, 0x141C0),
    "Limb 20": (Offsets.CHILD_LINK_LUT_DL_TORSO, 0x21130),
}

ADULT_START = 0x00F86000
ADULT_SIZE  = 0x00037800
CHILD_START = 0x00FBE000
CHILD_SIZE  = 0x0002CF80
