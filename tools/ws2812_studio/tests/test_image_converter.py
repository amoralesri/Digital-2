from PIL import Image

from ws2812_studio.services.image_converter import ImageImportOptions, convert_image_to_frame


def test_convert_image_to_8x8_frame(tmp_path):
    path = tmp_path / "image.png"
    image = Image.new("RGB", (16, 16), (10, 20, 30))
    image.save(path)
    frame = convert_image_to_frame(path, ImageImportOptions(fit="stretch"))
    assert len(frame.pixels) == 64
    assert frame.pixels[0] == (10, 20, 30)


def test_transparency_background(tmp_path):
    path = tmp_path / "image.png"
    image = Image.new("RGBA", (8, 8), (255, 0, 0, 0))
    image.save(path)
    frame = convert_image_to_frame(path, ImageImportOptions(background=(1, 2, 3)))
    assert frame.pixels[0] == (1, 2, 3)
