import gzip
import Rom
from ntype import BigStream


# Handle 3.0 website patches.
# Re-implementation of https://github.com/mhinds7/minibsdiff
def apply_mbsdiff_patch_file(rom: Rom, file):
    with gzip.open(file, 'r') as stream:
        patch_data = BigStream(stream.read())

    if patch_data.read_bytes(length=8) != b'MBSDIF43':  # MBSDIFF header
        raise Exception("Patch file does not have a valid header. Aborting.")

    ctrl_len = mbsdiff_read_int64(patch_data)
    data_len = mbsdiff_read_int64(patch_data)
    new_size = mbsdiff_read_int64(patch_data)

    if ctrl_len < 0 or data_len < 0 or new_size < 0:
        raise Exception("Patch file is invalid. Aborting.")

    original_size = len(rom.original.buffer)
    size_difference = new_size - len(rom.buffer)
    if size_difference > 0:
        rom.append_bytes([0] * size_difference)

    ctrl_block = [0] * 3
    ctrl_block_address = 32
    diff_block_address = ctrl_block_address + ctrl_len
    extra_block_address = diff_block_address + data_len

    old_pos = new_pos = 0
    while new_pos < new_size:
        ctrl_block[0] = mbsdiff_read_int64(patch_data, ctrl_block_address)
        ctrl_block[1] = mbsdiff_read_int64(patch_data)
        ctrl_block[2] = mbsdiff_read_int64(patch_data)
        ctrl_block_address += 24

        if ctrl_block[0] > 0:
            # Sanity check.
            if new_pos + ctrl_block[0] > new_size:
                raise Exception("Patch file is invalid. Aborting.")

            # Read diff bytes.
            diff_bytes = patch_data.read_bytes(diff_block_address, ctrl_block[0])
            diff_block_address += ctrl_block[0]

            # Check for differences.
            for i, diff_byte in enumerate(diff_bytes):
                if old_pos + i > original_size:
                    break
                original_byte = rom.original.read_byte(old_pos + i)
                current_byte = rom.read_byte(new_pos + i)
                new_byte = (original_byte + diff_byte) & 0xFF
                if new_byte != current_byte:
                    rom.write_byte(new_pos + i, new_byte)

            # Increment positions.
            old_pos += ctrl_block[0]
            new_pos += ctrl_block[0]

        if ctrl_block[1] > 0:
            # Sanity check.
            if new_pos + ctrl_block[1] > new_size:
                raise Exception("Patch file is invalid. Aborting.")

            # Read extra bytes.
            extra_bytes = patch_data.read_bytes(extra_block_address, ctrl_block[1])
            extra_block_address += ctrl_block[1]

            # Check for differences.
            for i, extra_byte in enumerate(extra_bytes):
                current_byte = rom.read_byte(new_pos + i)
                if extra_byte != current_byte:
                    rom.write_byte(new_pos + i, extra_byte)

        # Increment positions.
        old_pos += ctrl_block[2]
        new_pos += ctrl_block[1]

    # Patch completed, now setup stuff in Rom object and patch version number if necessary.
    rom.changed_dma = {}
    rom.scan_dmadata_update(assume_move=True)
    version_bytes = rom.read_bytes(0x35, 3)
    if version_bytes[0] == 0 and version_bytes[1] == 0 and version_bytes[2] == 0:
        # No version bytes, so assume this is a 3.0 patch.
        version_bytes[0] = 3
        rom.write_bytes(0x35, version_bytes)
    # Force language to be English in the event a Japanese rom was submitted
    rom.write_byte(0x3E, 0x45)
    rom.force_patch.append(0x3E)


def mbsdiff_read_int64(patch_data: BigStream, position=None):
    buf = patch_data.read_bytes(position, 8)
    y = buf[7] & 0x7F
    y = y * 256
    y += buf[6]
    y = y * 256
    y += buf[5]
    y = y * 256
    y += buf[4]
    y = y * 256
    y += buf[3]
    y = y * 256
    y += buf[2]
    y = y * 256
    y += buf[1]
    y = y * 256
    y += buf[0]

    if buf[7] & 0x80:
        y = -y

    return y
