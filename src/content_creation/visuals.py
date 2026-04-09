from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageFilter


SQUARE_SIZE = (1080, 1080)
PORTRAIT_SIZE = (1080, 1350)
LANDSCAPE_SIZE = (1600, 900)


def render_social_images(thumbnail_path: Path, output_dir: Path) -> None:
    with Image.open(thumbnail_path) as image:
        base = image.convert("RGB")
        square = cover_resize(base, SQUARE_SIZE)
        portrait = build_portrait_from_thumbnail(base)
        landscape = cover_resize(base, LANDSCAPE_SIZE)
        square.save(output_dir / "social_image_1x1.jpg", quality=92)
        portrait.save(output_dir / "social_image_4x5.jpg", quality=92)
        landscape.save(output_dir / "social_image_16x9.jpg", quality=92)


def build_portrait_from_thumbnail(image: Image.Image) -> Image.Image:
    background = cover_resize(image, PORTRAIT_SIZE).filter(ImageFilter.GaussianBlur(radius=18))
    foreground_width = int(PORTRAIT_SIZE[0] * 0.88)
    foreground_height = int(foreground_width * 9 / 16)
    foreground = cover_resize(image, (foreground_width, foreground_height))
    x = (PORTRAIT_SIZE[0] - foreground_width) // 2
    y = (PORTRAIT_SIZE[1] - foreground_height) // 2
    background.paste(foreground, (x, y))
    return background


def cover_resize(image: Image.Image, target_size: tuple[int, int]) -> Image.Image:
    target_width, target_height = target_size
    source_width, source_height = image.size
    source_ratio = source_width / source_height
    target_ratio = target_width / target_height

    if source_ratio > target_ratio:
        scaled_height = target_height
        scaled_width = int(target_height * source_ratio)
    else:
        scaled_width = target_width
        scaled_height = int(target_width / source_ratio)

    resized = image.resize((scaled_width, scaled_height), Image.Resampling.LANCZOS)
    left = max((scaled_width - target_width) // 2, 0)
    top = max((scaled_height - target_height) // 2, 0)
    return resized.crop((left, top, left + target_width, top + target_height))
