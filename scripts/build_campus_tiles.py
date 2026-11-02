"""Build fixed public map artwork into bounded-size, multiresolution tiles.

Run from the repository root: python scripts/build_campus_tiles.py
Requires Pillow. This processes project artwork, never user uploads.
"""
import json
from pathlib import Path
from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'frontend/public/assets/campus/qingdao-campus.jpg'
DEST = ROOT / 'frontend/public/assets/campus/tiles'
Image.MAX_IMAGE_PIXELS = 110_000_000


def main():
    DEST.mkdir(parents=True, exist_ok=True)
    with Image.open(SOURCE) as original:
        original.load()
        levels = []
        for level, divisor in enumerate((16, 8, 4, 2, 1)):
            width = (original.width + divisor - 1) // divisor
            height = (original.height + divisor - 1) // divisor
            image = original.resize((width, height), Image.Resampling.LANCZOS) if divisor > 1 else original
            folder = DEST / str(level)
            folder.mkdir(exist_ok=True)
            for row in range((height + 511) // 512):
                for col in range((width + 511) // 512):
                    image.crop((col * 512, row * 512, min((col + 1) * 512, width), min((row + 1) * 512, height))).save(
                        folder / f'{col}-{row}.webp', quality=92, method=4)
            if divisor == 8:
                image.save(DEST.parent / 'qingdao-preview.webp', quality=88, method=4)
            levels.append({'width': width, 'height': height})
        manifest = {'width': original.width, 'height': original.height, 'tileSize': 512, 'levels': levels}
    (DEST / 'manifest.json').write_text(json.dumps(manifest), encoding='utf-8')
    files = list(DEST.rglob('*.webp'))
    print(f'{len(files)} tiles, {sum(p.stat().st_size for p in files) / 1024 / 1024:.1f} MiB')


if __name__ == '__main__':
    main()
