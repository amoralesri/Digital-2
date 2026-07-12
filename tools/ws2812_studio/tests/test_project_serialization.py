from ws2812_studio.models.frame import Frame
from ws2812_studio.models.project import Project
from ws2812_studio.services.mapping import MatrixMapping


def test_project_roundtrip(tmp_path):
    project = Project(
        mapping=MatrixMapping(serpentine=True, origin="bottom_left"),
        brightness=128,
    )
    project.animation.frames[0] = Frame.blank((1, 2, 3), duration_ms=123)
    path = tmp_path / "demo.ws2812project"
    project.save(path)
    loaded = Project.load(path)
    assert loaded.brightness == 128
    assert loaded.mapping.serpentine is True
    assert loaded.mapping.origin == "bottom_left"
    assert loaded.animation.frames[0].pixels[0] == (1, 2, 3)
    assert loaded.animation.frames[0].duration_ms == 123
