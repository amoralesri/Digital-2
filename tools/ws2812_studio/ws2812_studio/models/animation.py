from __future__ import annotations

from dataclasses import dataclass, field

from .frame import Frame


@dataclass
class Animation:
    frames: list[Frame] = field(default_factory=lambda: [Frame.blank()])
    loop: bool = True
    speed: float = 1.0

    def add_frame(self, frame: Frame | None = None) -> None:
        self.frames.append(frame.copy() if frame else Frame.blank())

    def duplicate_frame(self, index: int) -> None:
        self.frames.insert(index + 1, self.frames[index].copy())

    def remove_frame(self, index: int) -> None:
        if len(self.frames) <= 1:
            self.frames[0] = Frame.blank()
            return
        del self.frames[index]

    @property
    def total_duration_ms(self) -> int:
        return sum(frame.duration_ms for frame in self.frames)
