#!/usr/bin/env python3
"""Software trace for the restoring divider implemented in div.v."""

import argparse


def parse_u16(value):
    number = int(value, 0)
    if number < 0 or number > 0xFFFF:
        raise argparse.ArgumentTypeError("value must fit in 16 bits")
    return number


def main():
    parser = argparse.ArgumentParser(
        description="Simulate the same 16-bit division algorithm used by div.v"
    )
    parser.add_argument("op_a", nargs="?", type=parse_u16, default=0xC86C)
    parser.add_argument("op_b", nargs="?", type=parse_u16, default=0x00CA)
    args = parser.parse_args()

    if args.op_b == 0:
        raise SystemExit("Division by zero is not supported by the hardware core")

    a = args.op_a
    b = args.op_b
    count = 16

    print(f"Dividend op_A = 0x{args.op_a:04X} ({args.op_a})")
    print(f"Divisor  op_B = 0x{args.op_b:04X} ({args.op_b})")
    print()
    print("iter state          count A[31:16] A[15:0] A_minus_B bit_q")
    print("---- -------------- ----- -------- -------- --------- -----")

    for iteration in range(1, 17):
        a = (a << 1) & 0xFFFFFFFF
        count -= 1
        upper = (a >> 16) & 0xFFFF
        lower = a & 0xFFFF
        a_minus_b = (upper - b) & 0xFFFF
        negative = (a_minus_b & 0x8000) != 0

        print(
            f"{iteration:>4} SHIFT          {count:>5} "
            f"0x{upper:04X}   0x{lower:04X}   0x{a_minus_b:04X}    -"
        )

        if negative:
            bit_q = 0
            a &= 0xFFFFFFFE
        else:
            bit_q = 1
            a = (a & 0x0000FFFF) | (a_minus_b << 16)
            a |= 1

        print(
            f"{iteration:>4} CHECK_GREATER {count:>5} "
            f"0x{(a >> 16) & 0xFFFF:04X}   0x{a & 0xFFFF:04X}   "
            f"0x{a_minus_b:04X}    {bit_q}"
        )

    quotient = a & 0xFFFF
    remainder = (a >> 16) & 0xFFFF
    print()
    print(f"Quotient  = 0x{quotient:04X} ({quotient})")
    print(f"Remainder = 0x{remainder:04X} ({remainder})")
    print(f"Check     = {args.op_b} * {quotient} + {remainder} = "
          f"{args.op_b * quotient + remainder}")


if __name__ == "__main__":
    main()
