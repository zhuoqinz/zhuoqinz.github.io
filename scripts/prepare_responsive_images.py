"""Create responsive AVIF/WebP display assets; keep original images for zooming.

Paper AVIFs use quality 90 and full-resolution chroma (4:4:4) to retain small
colored text and diagram edges. Lossless WebP remains the compatibility fallback.
Requires Pillow with AVIF support. Original PNGs and the portrait are unchanged.
"""
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / "assets/img/responsive"


def variants(source, widths, *, avif=False):
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
            if avif:
                modern = target.with_suffix(".avif")
                resized.save(modern, "AVIF", quality=90, subsampling="4:4:4",
                             speed=6, max_threads=2)
                with Image.open(modern) as encoded:
                    assert encoded.size == resized.size
                print(f"{modern.name}: {size}, {modern.stat().st_size:,} bytes")


if __name__ == "__main__":
    DEST.mkdir(parents=True, exist_ok=True)
    variants("assets/img/portrait-shirt.webp", (220, 440, 660))
    for name in ("interactive-omni", "children", "rejection-enhanced", "soccer", "cognitive"):
        # Cover the ~180-250 CSS-pixel desktop figures at 1x/2x/3x without
        # rounding every retina request up to a much larger 640/960px image.
        widths = (240, 320, 480, 560, 640, 800, 960, 2000)
        # Their original-resolution WebPs are smaller than the 800px variants.
        if name in ("children", "cognitive"):
            widths = tuple(width for width in widths if width != 800)
        variants(f"assets/img/papers/{name}.png", widths, avif=True)
