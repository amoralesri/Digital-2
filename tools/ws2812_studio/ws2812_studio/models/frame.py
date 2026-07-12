from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from ws2812_studio.constants import HEIGHT, LED_COUNT, WIDTH

Color = tuple[int, int, int]


def clamp_channel(value: int) -> int:
    return max(0, min(255, int(value)))


def normalize_color(color: Iterable[int]) -> Color:
    r, g, b = color
    return (clamp_channel(r), clamp_channel(g), clamp_channel(b))


@dataclass
class Frame:
    pixels: list[Color] = field(default_factory=lambda: [(0, 0, 0)] * LED_COUNT)
    duration_ms: int = 250

    def __post_init__(self) -> None:
        if len(self.pixels) != LED_COUNT:
            raise ValueError(f"Frame must contain exactly {LED_COUNT} pixels")
        self.pixels = [normalize_color(pixel) for pixel in self.pixels]
        self.duration_ms = max(1, int(self.duration_ms))

    @classmethod
    def blank(cls, color: Color = (0, 0, 0), duration_ms: int = 250) -> "Frame":
        return cls([normalize_color(color)] * LED_COUNT, duration_ms)

    def copy(self) -> "Frame":
        return Frame(list(self.pixels), self.duration_ms)

    def index(self, x: int, y: int) -> int:
        if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
            raise ValueError(f"Pixel coordinate out of range: {(x, y)}")
        return y * WIDTH + x

    def get_pixel(self, x: int, y: int) -> Color:
        return self.pixels[self.index(x, y)]

    def set_pixel(self, x: int, y: int, color: Color) -> None:
        self.pixels[self.index(x, y)] = normalize_color(color)

    def fill(self, color: Color) -> None:
        normalized = normalize_color(color)
        self.pixels = [normalized] * LED_COUNT

    def clear(self) -> None:
        self.fill((0, 0, 0))

    def to_rgb_bytes(self) -> bytes:
        data = bytearray()
        for r, g, b in self.pixels:
            data.extend((r, g, b))
        return bytes(data)

    @classmethod
    def from_rgb_bytes(cls, data: bytes, duration_ms: int = 250) -> "Frame":
        if len(data) != LED_COUNT * 3:
            raise ValueError("RGB frame payload must be 192 bytes")
        pixels = [(data[i], data[i + 1], data[i + 2]) for i in range(0, len(data), 3)]
        return cls(pixels, duration_ms)

    def to_json(self) -> dict:
        return {
            "duration_ms": self.duration_ms,
            "pixels": [list(pixel) for pixel in self.pixels],
        }

    @classmethod
    def from_json(cls, data: dict) -> "Frame":
        return cls(
            pixels=[tuple(pixel) for pixel in data["pixels"]],
            duration_ms=int(data.get("duration_ms", 250)),
        )
