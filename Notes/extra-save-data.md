This file documents parts of the OoT save data that go unused in vanilla but are used by the randomizer. **It may be incomplete.**

# Scene flags

The unused field (offset 0x10) of the permanent scene flags (save context + 0xd4 + 0x1c * scene ID) is used for the following purposes:

* Scrub Shuffle: Scenes 0x10–0x27
* Shopsanity: Scene 0x2C
* FW in both ages: Scenes 0x3E–0x47
* Triforce Hunt: Scene 0x48

# Shuffle Cows

The flags representing which cows have been talked to are stored in the collectibles field (offset 0x0c) of the permanent scene flags of the cow's respective scene:

* Jabu Jabus Belly MQ Cow: scene 0x02, bit 0100_0000
* KF Links House Cow: scene 0x34, bit 0100_0000
* LLR Stables Right Cow: scene 0x36, bit 0200_0000
* LLR Stables Left Cow: scene 0x36, bit 0100_0000
* Kak Impas House Cow: scene 0x37, bit 0100_0000
* HF Cow Grotto Cow: scene 0x37, bit 0200_0000
* DMT Cow Grotto Cow: scene 0x3e, bit 0100_0000
* LLR Tower Left Cow: scene 0x4c, bit 0200_0000
* LLR Tower Right Cow: scene 0x4c, bit 0100_0000
* GV Cow: scene 0x5a, bit 0100_0000
