.section .text
.globl start 
.globl blinker
.globl put_hello

calculator:

loopM:	
   li   sp,0x1000
   li   sp,0x1000

	la   a0, number
	call putstring
	call get_number      # first number
	call bcd2bin
    add  t1, a0, zero    # store first operator in t1

	la   a0, number
	call putstring
	call get_number      # second number
	call bcd2bin
    add  t3, a0, zero    # Store second operator in t3

	add  a0, t1, zero
	add  a1, t3, zero
	call test
	call bin2bcd
	j    loopM

.section .data
number:
	.asciz "\n\rNumber: "
operator:
	.asciz "\n\rOperator "
result:
	.asciz "\n\rResult = "
