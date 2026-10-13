#!/usr/bin/env python3
"""
prep_photo.py
Step 3a: Prepares source-photo.jpg for high-contrast, clean ASCII generation:
1. Removes the background with rembg (using lightweight u2netp ~4MB model) so the subject is isolated.
2. Boosts local contrast with OpenCV's CLAHE (contrast-limited adaptive histogram equalization).
3. Composites onto pure white so the background maps to the blank end of the ASCII ramp (white -> spaces).
Outputs: data/source-prepped.png
"""

import sys
from pathlib import Path
import cv2
import numpy as np
from PIL import Image

def prep_photo(input_path: Path, output_path: Path):
    print(f"📸 Loading {input_path}...")
    input_img = Image.open(input_path)
    
    # Try background removal with u2netp (fast ~4.7MB model)
    try:
        from rembg import remove, new_session
        print("✂️  Removing background using u2netp...")
        session = new_session("u2netp")
        no_bg = remove(input_img, session=session)
        rgba = np.array(no_bg)
        rgb = rgba[:, :, :3]
        alpha = rgba[:, :, 3]
    except Exception as e:
        print(f"⚠️  Background removal note ({e}), proceeding with full portrait enhancement...")
        rgb = np.array(input_img.convert("RGB"))
        alpha = np.ones((rgb.shape[0], rgb.shape[1]), dtype=np.uint8) * 255
    
    # Convert RGB to grayscale for CLAHE processing
    gray = cv2.cvtColor(rgb, cv2.COLOR_RGB2GRAY)
    
    print("✨ Boosting local contrast with CLAHE...")
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    
    print("⚪ Compositing onto pure white background...")
    alpha_norm = alpha.astype(float) / 255.0
    white_bg = np.ones_like(enhanced, dtype=float) * 255.0
    composited = (enhanced.astype(float) * alpha_norm + white_bg * (1.0 - alpha_norm)).astype(np.uint8)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    res_img = Image.fromarray(composited)
    res_img.save(output_path)
    print(f"✅ Saved prepped image to {output_path}")

def main():
    if len(sys.argv) > 1:
        inp = Path(sys.argv[1])
    else:
        inp = Path(__file__).parent.parent / "source-photo.jpg"
    
    if not inp.exists():
        print(f"❌ Error: {inp} not found!")
        sys.exit(1)
        
    out = Path(__file__).parent.parent / "data" / "source-prepped.png"
    prep_photo(inp, out)

if __name__ == "__main__":
    main()
