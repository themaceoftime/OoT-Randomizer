rand_seed_truth_spinner:
    addiu   sp, sp, -0x20
    sw      t0, 0x14(sp)
    sw      a0, 0x18(sp)
    sw      ra, 0x1C(sp)
    
    jal     seed_rng
    nop

    ; Displaced instruction
    lh      v0, 0x00B6(s0)

    lw      t0, 0x14(sp)
    lw      a0, 0x18(sp)
    lw      ra, 0x1C(sp)
    jr      ra
    addiu   sp, sp, 0x20
