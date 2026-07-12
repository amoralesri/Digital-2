from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageEnhance, ImageOps

from ws2812_studio.constants import HEIGHT, WIDTH
from ws2812_studio.models.frame import Frame


RESAMPLE_METHODS = {
    "nearest": Image.Resampling.NEAREST,
    "bilinear": Image.Resampling.BILINEAR,
    "bicubic": Image.Resampling.BICUBIC,
}


@dataclass
class ImageImportOptions:
    fit: str = "cover"
    resample: str = "nearest"
    brightness: float = 1.0
    contrast: float = 1.0
    saturation: float = 1.0
    gamma: float = 1.0
    rotate: int = 0
    mirror_x: bool = False
    mirror_y: bool = False
    background: tuple[int, int, int] = (0, 0, 0)


def _apply_gamma(image: Image.Image, gamma: float) -> Image.Image:
    if gamma == 1.0:
        return image
    lut = [min(255, int(((i / 255.0) ** (1.0 / gamma)) * 255.0 + 0.5)) for i in range(256)]
    return image.point(lut * len(image.getbands()))


def convert_image_to_frame(path: str | Path, options: ImageImportOptions | None = None) -> Frame:
    options = options or ImageImportOptions()
    image = Image.open(path).convert("RGBA")

    if options.rotate:
        image = image.rotate(-options.rotate, expand=True)
    if options.mirror_x:
        image = ImageOps.mirror(image)
    if options.mirror_y:
        image = ImageOps.flip(image)

    background = Image.new("RGBA", image.size, (*options.background, 255))
    image = Image.alpha_composite(background, image).convert("RGB")
    image = ImageEnhance.Brightness(image).enhance(options.brightness)
    image = ImageEnhance.Contrast(image).enhance(options.contrast)
    image = ImageEnhance.Color(image).enhance(options.saturation)
    image = _apply_gamma(image, max(0.1, options.gamma))

    resample = RESAMPLE_METHODS.get(options.resample, Image.Resampling.NEAREST)
    if options.fit == "stretch":
        resized = image.resize((WIDTH, HEIGHT), resample)
    else:
        source = image.copy()
        source.thumbnail((WIDTH, HEIGHT), resample)
        if options.fit == "contain":
            resized = Image.new("RGB", (WIDTH, HEIGHT), options.background)
            resized.paste(source, ((WIDTH - source.width) // 2, (HEIGHT - source.height) // 2))
        else:
            resized = ImageOps.fit(image, (WIDTH, HEIGHT), method=resample, centering=(0.5, 0.5))

    pixels = [resized.getpixel((x, y)) for y in range(HEIGHT) for x in range(WIDTH)]
    return Frame(pixels=pixels)
