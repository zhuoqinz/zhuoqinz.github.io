"""Create lossless WebP display variants; keep original images for zooming."""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "assets/img/responsive"


def variants(source, widths):
    with Image.open(ROOT / source) as original:
        image = original.convert("RGB" if original.mode != "RGBA" else "RGBA")
        for width in sorted(set(min(width, image.width) for width in widths)):
            size = (width, round(image.height * width / image.width))
            resized = image.resize(size, Image.Resampling.LANCZOS)
            target = DEST / f"{Path(source).stem}-{width}.webp"
            resized.save(target, "WEBP", lossless=True, method=6)
            # WebP encoding must preserve every pixel of the resized image.
            with Image.open(target) as encoded:
                assert encoded.convert(resized.mode).tobytes() == resized.tobytes()
            print(f"{target.name}: {size}, {target.stat().st_size:,} bytes")


if __name__ == "__main__":
    DEST.mkdir(parents=True, exist_ok=True)
    variants("assets/img/portrait-shirt.webp", (220, 440, 660))
    for name in ("interactive-omni", "children", "rejection-enhanced", "soccer", "cognitive"):
        variants(f"assets/img/papers/{name}.png", (320, 640, 960, 2000))
