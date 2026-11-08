"""Turn cloth photos into a discoloration index.

How it works:
1. Load the photo and crop the center (where the cloth is).
2. Correct for lighting by scaling so the brightest part is pure white.
3. Convert to CIELAB and measure lightness (L*, 0 = black, 100 = white).
4. Compare to the clean blank cloth: index = blank lightness - sample lightness.
   Higher index = dirtier cloth.

Run from the repo root:
    python src/discoloration.py
"""

from pathlib import Path

import cv2
import numpy as np
import pandas as pd

PHOTO_DIR = Path("data/photos")
BLANK_DIR = Path("data/blanks")
OUTPUT = Path("data/discoloration.csv")
IMAGE_TYPES = {".jpg", ".jpeg", ".png"}  # iPhone .heic photos must be converted to .jpg first

CROP_FRACTION = 0.5     # use the middle 50% of the image
DARK_THRESHOLD = 10     # pixels this many L* units darker than the blank count as "dust"


def load_and_prepare(path):
    """Load an image, crop the center, and correct for lighting."""
    img = cv2.imread(str(path))
    if img is None:
        raise ValueError(f"Could not read {path}")

    h, w = img.shape[:2]
    ch, cw = int(h * CROP_FRACTION), int(w * CROP_FRACTION)
    top, left = (h - ch) // 2, (w - cw) // 2
    img = img[top:top + ch, left:left + cw]

    # Lighting correction: scale so the brightest 1% of pixels become white
    img = img.astype(np.float32)
    bright = np.percentile(img, 99)
    img = np.clip(img * (255.0 / bright), 0, 255).astype(np.uint8)
    return img


def lightness(img):
    """Return the L* (lightness) channel scaled to 0-100."""
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    return lab[:, :, 0].astype(np.float32) * (100.0 / 255.0)


def measure(path, blank_lightness):
    L = lightness(load_and_prepare(path))
    return {
        "photo_file": path.name,
        "mean_lightness": round(float(L.mean()), 2),
        "discoloration_index": round(blank_lightness - float(L.mean()), 2),
        "dust_pixel_pct": round(float((L < blank_lightness - DARK_THRESHOLD).mean() * 100), 2),
    }


def images_in(folder):
    return sorted(p for p in folder.iterdir() if p.suffix.lower() in IMAGE_TYPES)


def main():
    blanks = images_in(BLANK_DIR)
    if not blanks:
        raise SystemExit("No blank photos found in data/blanks/")
    blank_lightness = float(np.mean([lightness(load_and_prepare(b)).mean() for b in blanks]))
    print(f"Clean cloth lightness (average of {len(blanks)} blanks): {blank_lightness:.2f}")

    photos = images_in(PHOTO_DIR)
    if not photos:
        raise SystemExit("No sample photos found in data/photos/")

    results = pd.DataFrame([measure(p, blank_lightness) for p in photos])
    results.to_csv(OUTPUT, index=False)
    print(results.to_string(index=False))
    print(f"\nSaved {len(results)} results to {OUTPUT}")


if __name__ == "__main__":
    main()
