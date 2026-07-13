from __future__ import annotations


def clamp_channel(value: int) -> int:
    return max(0, min(255, int(value)))


def apply_brightness(color: tuple[int, int, int], brightness: int = 255) -> tuple[int, int, int]:
    scale = clamp_channel(brightness)
    r, g, b = color
    return (
        clamp_channel(r) * scale // 255,
        clamp_channel(g) * scale // 255,
        clamp_channel(b) * scale // 255,
    )


def rgb_to_ws2812_word(r: int, g: int, b: int, brightness: int = 255) -> int:
    rr, gg, bb = apply_brightness((r, g, b), brightness)
    return (gg << 16) | (rr << 8) | bb


def rgb_to_ws2812_bytes(r: int, g: int, b: int, brightness: int = 255) -> bytes:
    rr, gg, bb = apply_brightness((r, g, b), brightness)
    return bytes((gg, rr, bb))
