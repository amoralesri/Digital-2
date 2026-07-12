from __future__ import annotations

from dataclasses import dataclass

from ws2812_studio.constants import HEIGHT, LED_COUNT, WIDTH


@dataclass(frozen=True)
class MatrixMapping:
    serpentine: bool = False
    origin: str = "top_left"
    rotation: int = 0
    mirror_x: bool = False
    mirror_y: bool = False

    def _transform(self, x: int, y: int) -> tuple[int, int]:
        if not (0 <= x < WIDTH and 0 <= y < HEIGHT):
            raise ValueError(f"Coordinate out of range: {(x, y)}")

        if self.mirror_x:
            x = WIDTH - 1 - x
        if self.mirror_y:
            y = HEIGHT - 1 - y

        rot = self.rotation % 360
        if rot == 90:
            x, y = HEIGHT - 1 - y, x
        elif rot == 180:
            x, y = WIDTH - 1 - x, HEIGHT - 1 - y
        elif rot == 270:
            x, y = y, WIDTH - 1 - x
        elif rot != 0:
            raise ValueError("Rotation must be 0, 90, 180 or 270")

        if self.origin == "top_right":
            x = WIDTH - 1 - x
        elif self.origin == "bottom_left":
            y = HEIGHT - 1 - y
        elif self.origin == "bottom_right":
            x = WIDTH - 1 - x
            y = HEIGHT - 1 - y
        elif self.origin != "top_left":
            raise ValueError(f"Unsupported origin: {self.origin}")

        return x, y

    def logical_to_physical(self, x: int, y: int) -> int:
        x, y = self._transform(x, y)
        if self.serpentine and (y % 2):
            x = WIDTH - 1 - x
        index = y * WIDTH + x
        if not 0 <= index < LED_COUNT:
            raise ValueError(f"Physical index out of range: {index}")
        return index

    def reorder_pixels(self, pixels: list[tuple[int, int, int]]) -> list[tuple[int, int, int]]:
        if len(pixels) != LED_COUNT:
            raise ValueError("Expected 64 logical pixels")
        physical = [(0, 0, 0)] * LED_COUNT
        for y in range(HEIGHT):
            for x in range(WIDTH):
                physical[self.logical_to_physical(x, y)] = pixels[y * WIDTH + x]
        return physical

    def to_dict(self) -> dict:
        return {
            "serpentine": self.serpentine,
            "origin": self.origin,
            "rotation": self.rotation,
            "mirror_x": self.mirror_x,
            "mirror_y": self.mirror_y,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MatrixMapping":
        return cls(
            serpentine=bool(data.get("serpentine", False)),
            origin=data.get("origin", "top_left"),
            rotation=int(data.get("rotation", 0)),
            mirror_x=bool(data.get("mirror_x", False)),
            mirror_y=bool(data.get("mirror_y", False)),
        )
