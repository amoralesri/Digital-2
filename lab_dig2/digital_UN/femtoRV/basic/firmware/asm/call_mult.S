.section .text

loopM:

li   sp,0x2000

    li   a0, 5
    li   a1, 4
    call mult_hw
    j    loopM
