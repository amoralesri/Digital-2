from __future__ import annotations

from dataclasses import dataclass, field
import json
from pathlib import Path

from ws2812_studio.constants import HEIGHT, PROJECT_FORMAT_VERSION, WIDTH
from ws2812_studio.services.mapping import MatrixMapping

from .animation import Animation
from .frame import Frame


@dataclass
class Project:
    animation: Animation = field(default_factory=Animation)
    mapping: MatrixMapping = field(default_factory=MatrixMapping)
    brightness: int = 255
    favorites: list[tuple[int, int, int]] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "version": PROJECT_FORMAT_VERSION,
            "width": WIDTH,
            "height": HEIGHT,
            "brightness": self.brightness,
            "mapping": self.mapping.to_dict(),
            "favorites": [list(color) for color in self.favorites],
            "metadata": self.metadata,
            "playback": {
                "loop": self.animation.loop,
                "speed": self.animation.speed,
            },
            "frames": [frame.to_json() for frame in self.animation.frames],
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Project":
        if int(data.get("version", 0)) > PROJECT_FORMAT_VERSION:
            raise ValueError("Unsupported WS2812 project format version")
        frames = [Frame.from_json(frame) for frame in data.get("frames", [])] or [Frame.blank()]
        playback = data.get("playback", {})
        return cls(
            animation=Animation(
                frames=frames,
                loop=bool(playback.get("loop", True)),
                speed=float(playback.get("speed", 1.0)),
            ),
            mapping=MatrixMapping.from_dict(data.get("mapping", {})),
            brightness=int(data.get("brightness", 255)),
            favorites=[tuple(color) for color in data.get("favorites", [])],
            metadata=dict(data.get("metadata", {})),
        )

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path: str | Path) -> "Project":
        return cls.from_dict(json.loads(Path(path).read_text(encoding="utf-8")))
