import pytest

from ws2812_studio.models.animation import Animation
from ws2812_studio.models.frame import Frame
from ws2812_studio.models.project import Project
from ws2812_studio.services.codegen import (
    project_to_grb_frames,
    render_header,
    render_source,
    rgb_to_grb_word,
    summarize_project,
    validate_project,
    write_generated_animation,
)
from ws2812_studio.services.mapping import MatrixMapping


def test_rgb_to_grb_word_and_brightness():
    assert rgb_to_grb_word(1, 2, 3) == 0x00020103
    assert rgb_to_grb_word(100, 50, 10, brightness=128) == 0x00193205


def test_single_frame_led0_led63_and_durations(tmp_path):
    frame = Frame.blank()
    frame.set_pixel(0, 0, (255, 0, 0))
    frame.set_pixel(7, 7, (0, 0, 255))
    frame.duration_ms = 777
    project = Project(animation=Animation(frames=[frame], loop=False))

    frames = project_to_grb_frames(project)
    assert len(frames) == 1
    assert len(frames[0]) == 64
    assert frames[0][0] == 0x0000FF00
    assert frames[0][63] == 0x000000FF

    summary = write_generated_animation(project, tmp_path)
    assert summary.frame_count == 1
    assert summary.data_bytes == 256
    assert "#define WS2812_ANIMATION_LOOP 0u" in (tmp_path / "generated_animation.h").read_text()
    assert "777u" in (tmp_path / "generated_animation.c").read_text()


def test_multiple_frames_serpentine_mapping_and_reproducible_output():
    frame = Frame.blank()
    frame.set_pixel(0, 1, (0, 255, 0))
    project = Project(
        animation=Animation(frames=[frame, Frame.blank((1, 2, 3), duration_ms=123)], loop=True),
        mapping=MatrixMapping(serpentine=True),
    )
    frames = project_to_grb_frames(project)
    assert frames[0][15] == 0x00FF0000
    assert render_source(project) == render_source(project)
    assert "#define WS2812_ANIMATION_FRAME_COUNT 2u" in render_header(project)


def test_validation_rejects_empty_and_bad_frame():
    project = Project()
    project.animation.frames = []
    with pytest.raises(ValueError, match="no contiene frames"):
        validate_project(project)

    bad = Project(animation=Animation(frames=[Frame.blank()]))
    bad.animation.frames[0].pixels = bad.animation.frames[0].pixels[:-1]
    with pytest.raises(ValueError, match="64"):
        validate_project(bad)


def test_memory_estimate():
    project = Project(animation=Animation(frames=[Frame.blank(), Frame.blank(), Frame.blank()]))
    summary = summarize_project(project)
    assert summary.data_bytes == 3 * 64 * 4
    assert summary.total_duration_ms == 750
