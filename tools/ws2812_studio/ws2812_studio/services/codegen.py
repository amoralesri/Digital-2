from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from ws2812_studio.constants import LED_COUNT
from ws2812_studio.models.project import Project
from ws2812_studio.services.color_order import rgb_to_ws2812_word


@dataclass(frozen=True)
class AnimationBuildSummary:
    frame_count: int
    led_count: int
    data_bytes: int
    total_duration_ms: int
    loop: bool


def rgb_to_grb_word(r: int, g: int, b: int, brightness: int = 255) -> int:
    return rgb_to_ws2812_word(r, g, b, brightness)


def project_to_grb_frames(project: Project) -> list[list[int]]:
    validate_project(project)
    brightness = max(0, min(255, int(project.brightness)))
    frames: list[list[int]] = []
    for frame in project.animation.frames:
        mapped = project.mapping.reorder_pixels(frame.pixels)
        frames.append([rgb_to_grb_word(r, g, b, brightness) for r, g, b in mapped])
    return frames


def summarize_project(project: Project) -> AnimationBuildSummary:
    validate_project(project)
    frame_count = len(project.animation.frames)
    return AnimationBuildSummary(
        frame_count=frame_count,
        led_count=LED_COUNT,
        data_bytes=frame_count * LED_COUNT * 4,
        total_duration_ms=project.animation.total_duration_ms,
        loop=project.animation.loop,
    )


def validate_project(project: Project) -> None:
    if not project.animation.frames:
        raise ValueError("El proyecto no contiene frames.")
    for index, frame in enumerate(project.animation.frames):
        if len(frame.pixels) != LED_COUNT:
            raise ValueError(f"El frame {index} no contiene exactamente {LED_COUNT} pixeles.")
        if frame.duration_ms <= 0:
            raise ValueError(f"El frame {index} tiene una duracion invalida.")


def render_header(project: Project) -> str:
    summary = summarize_project(project)
    return "\n".join(
        [
            "#ifndef GENERATED_ANIMATION_H",
            "#define GENERATED_ANIMATION_H",
            "",
            "#include <stdint.h>",
            "",
            f"#define WS2812_ANIMATION_FRAME_COUNT {summary.frame_count}u",
            f"#define WS2812_ANIMATION_LOOP {1 if summary.loop else 0}u",
            f"#define WS2812_ANIMATION_LED_COUNT {summary.led_count}u",
            f"#define WS2812_ANIMATION_DATA_BYTES {summary.data_bytes}u",
            "",
            "extern const uint32_t ws2812_animation_frames[WS2812_ANIMATION_FRAME_COUNT][WS2812_ANIMATION_LED_COUNT];",
            "extern const uint32_t ws2812_frame_durations_ms[WS2812_ANIMATION_FRAME_COUNT];",
            "",
            "#endif",
            "",
        ]
    )


def render_source(project: Project) -> str:
    frames = project_to_grb_frames(project)
    lines = [
        '#include "generated_animation.h"',
        "",
        "const uint32_t ws2812_animation_frames[WS2812_ANIMATION_FRAME_COUNT][WS2812_ANIMATION_LED_COUNT] = {",
    ]
    for frame in frames:
        lines.append("    {")
        for offset in range(0, LED_COUNT, 8):
            words = ", ".join(f"0x{word:08x}u" for word in frame[offset:offset + 8])
            lines.append(f"        {words},")
        lines.append("    },")
    lines.extend(
        [
            "};",
            "",
            "const uint32_t ws2812_frame_durations_ms[WS2812_ANIMATION_FRAME_COUNT] = {",
        ]
    )
    durations = [max(1, int(frame.duration_ms)) for frame in project.animation.frames]
    for offset in range(0, len(durations), 8):
        values = ", ".join(f"{duration}u" for duration in durations[offset:offset + 8])
        lines.append(f"    {values},")
    lines.extend(["};", ""])
    return "\n".join(lines)


def write_generated_animation(project: Project, output_dir: str | Path) -> AnimationBuildSummary:
    output = Path(output_dir)
    if not output.exists():
        raise FileNotFoundError(f"No existe el directorio de firmware: {output}")
    (output / "generated_animation.h").write_text(render_header(project), encoding="utf-8")
    (output / "generated_animation.c").write_text(render_source(project), encoding="utf-8")
    return summarize_project(project)
