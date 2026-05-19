.section .text

loopM:

li   sp,0x2000

    li   a0, 12
    li   a1, 12
    call div_hw
    j    loopM