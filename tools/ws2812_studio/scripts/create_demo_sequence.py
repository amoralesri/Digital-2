#!/usr/bin/env python3
from __future__ import annotations

import argparse
from pathlib import Path
import sys


def _bootstrap_imports() -> None:
    repo_root = Path(__file__).resolve().parents[3]
    sys.path.insert(0, str(repo_root / "tools" / "ws2812_studio"))


_bootstrap_imports()

from ws2812_studio.models.animation import Animation
from ws2812_studio.models.frame import Frame
from ws2812_studio.models.project import Project
from ws2812_studio.services.codegen import write_generated_animation


LOW_RED = (24, 0, 0)
LOW_GREEN = (0, 24, 0)
LOW_BLUE = (0, 0, 24)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
OFF = (0, 0, 0)


def frame_from_rows(rows: list[list[tuple[int, int, int]]], duration_ms: int = 250) -> Frame:
    pixels = [pixel for row in rows for pixel in row]
    return Frame(pixels=pixels, duration_ms=duration_ms)


def single_led(index: int, color: tuple[int, int, int], duration_ms: int = 450) -> Frame:
    frame = Frame.blank(OFF, duration_ms)
    x = index % 8
    y = index // 8
    frame.set_pixel(x, y, color)
    return frame


def solid(color: tuple[int, int, int], duration_ms: int = 350) -> Frame:
    return Frame.blank(color, duration_ms)


def row_frame(row: int, color: tuple[int, int, int], duration_ms: int = 160) -> Frame:
    frame = Frame.blank(OFF, duration_ms)
    for x in range(8):
        frame.set_pixel(x, row, color)
    return frame


def column_frame(column: int, color: tuple[int, int, int], duration_ms: int = 160) -> Frame:
    frame = Frame.blank(OFF, duration_ms)
    for y in range(8):
        frame.set_pixel(column, y, color)
    return frame


def checkerboard(first: tuple[int, int, int], second: tuple[int, int, int], duration_ms: int = 350) -> Frame:
    rows = []
    for y in range(8):
        row = []
        for x in range(8):
            row.append(first if (x + y) % 2 == 0 else second)
        rows.append(row)
    return frame_from_rows(rows, duration_ms)


def diagonal_sweep(step: int, duration_ms: int = 110) -> Frame:
    frame = Frame.blank(OFF, duration_ms)
    for y in range(8):
        x = (step + y) % 8
        frame.set_pixel(x, y, (36, 36, 36))
    return frame


def build_demo_project() -> Project:
    frames = [
        Frame.blank(OFF, 300),
        single_led(0, LOW_GREEN),
        single_led(63, LOW_GREEN),
        solid(RED),
        solid(GREEN),
        solid(BLUE),
    ]
    frames.extend(row_frame(row, RED) for row in range(8))
    frames.extend(column_frame(column, BLUE) for column in range(8))
    frames.append(checkerboard(BLUE, GREEN))
    frames.append(checkerboard(GREEN, BLUE))
    frames.extend(diagonal_sweep(step) for step in range(8))
    return Project(animation=Animation(frames=frames, loop=True), brightness=96)


def main() -> int:
    repo_root = Path(__file__).resolve().parents[3]
    parser = argparse.ArgumentParser(description="Create the original WS2812 demo sequence.")
    parser.add_argument(
        "--project",
        default=str(repo_root / "tools" / "ws2812_studio" / "examples" / "demo_sequence.ws2812project"),
        help="Output .ws2812project path",
    )
    parser.add_argument(
        "--emit-firmware",
        action="store_true",
        help="Also overwrite Litex/NO_bios_fw_dma/generated_animation.c and .h",
    )
    args = parser.parse_args()

    project = build_demo_project()
    project_path = Path(args.project)
    project_path.parent.mkdir(parents=True, exist_ok=True)
    project.save(project_path)
    print(f"Proyecto demo escrito en: {project_path}")

    if args.emit_firmware:
        firmware_dir = repo_root / "Litex" / "NO_bios_fw_dma"
        summary = write_generated_animation(project, firmware_dir)
        print(f"Firmware generado: {summary.frame_count} frames, {summary.total_duration_ms} ms")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
