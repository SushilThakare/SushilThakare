#!/usr/bin/env python3
"""
make_ascii_svg.py
Converts data/source-prepped.png (or any prepped image) into an animated monochrome ASCII SVG:
- Grid: ~100 columns x 53 rows
- Density ramp: " .`:-=+*cs#%@" (bright -> dark)
- Monochrome light-gray glyphs on dark background
- SMIL horizontal clip wipe with a block cursor riding each row from top to bottom
- Matches dimensions of 370x340 to align with info-card.svg and the 860px layout
"""

import sys
from pathlib import Path
from PIL import Image
import numpy as np

OUTPUT = Path(__file__).parent.parent / "profile-ascii.svg"
DEFAULT_INPUT = Path(__file__).parent.parent / "data" / "source-prepped.png"

# Guide ramp: bright (sparse) -> dark (dense)
RAMP = " .`:-=+*cs#%@"

# Layout constants
W, H = 370, 340
HEADER_H = 38
PAD_X = 14
PAD_Y = 10

# Monospace font settings for 100 columns x 53 rows
COLS = 100
ROWS = 52
FONT_SIZE = 5.2
CHAR_W = 3.42
LINE_H = 5.4

# Terminal palette
BG_OUTER = "#0d1117"
BG_INNER = "#161b22"
BORDER = "#30363d"
TEXT_COLOR = "#c9d1d9"       # Clean monochrome light-gray
CURSOR_COLOR = "#58a6ff"     # Subtle terminal cursor
RED_DOT = "#ff5f57"
YEL_DOT = "#febc2e"
GRN_DOT = "#28c840"
MUTED = "#6e7681"

def image_to_ascii(image_path: Path):
    img = Image.open(image_path).convert("L")
    img_resized = img.resize((COLS, ROWS), Image.Resampling.LANCZOS)
    arr = np.array(img_resized)
    
    ascii_rows = []
    ramp_len = len(RAMP)
    
    # Prepped image: subject is darker than pure white background (255)
    # Bright (255) maps to index 0 (" "), Dark (0) maps to index -1 ("@")
    for row in arr:
        row_str = []
        for px in row:
            # px is 0..255. Invert so 255 (white bg) -> 0 (space)
            inverted = 255 - px
            idx = int(inverted / 255.0 * (ramp_len - 1))
            row_str.append(RAMP[idx])
        # Replace xml special chars
        escaped_row = "".join(row_str).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        ascii_rows.append(escaped_row)
    return ascii_rows

def build_animated_svg(rows: list) -> str:
    total_rows = len(rows)
    total_time = 2.4  # seconds for full portrait reveal
    row_dur = total_time / total_rows
    
    content_w = COLS * CHAR_W
    
    clips = []
    text_elements = []
    
    start_x = PAD_X
    start_y = HEADER_H + PAD_Y + 4
    
    for i, row in enumerate(rows):
        y = start_y + i * LINE_H
        row_start = i * row_dur
        clip_id = f"clip-r{i}"
        
        # SMIL animated clip path for this row
        clips.append(f'''    <clipPath id="{clip_id}">
      <rect x="{start_x}" y="{y - FONT_SIZE + 1:.1f}" width="0" height="{LINE_H:.1f}">
        <animate attributeName="width" from="0" to="{content_w:.1f}" dur="{row_dur:.3f}s" begin="{row_start:.3f}s" fill="freeze" calcMode="linear"/>
      </rect>
    </clipPath>''')
        
        # Text element clipped
        text_elements.append(
            f'    <text x="{start_x}" y="{y:.1f}" clip-path="url(#{clip_id})" '
            f'font-family="monospace, Courier New" font-size="{FONT_SIZE:.1f}" fill="{TEXT_COLOR}">'
            f'{row}</text>'
        )
        
        # Cursor riding the row wipe
        text_elements.append(
            f'    <rect x="{start_x}" y="{y - FONT_SIZE + 1.2:.1f}" width="4" height="{LINE_H - 1:.1f}" fill="{CURSOR_COLOR}" opacity="0">'
            f'<animate attributeName="opacity" values="1;1;0" keyTimes="0;0.99;1" dur="{row_dur:.3f}s" begin="{row_start:.3f}s" fill="freeze"/>'
            f'<animate attributeName="x" from="{start_x}" to="{start_x + content_w:.1f}" dur="{row_dur:.3f}s" begin="{row_start:.3f}s" fill="freeze" calcMode="linear"/>'
            f'</rect>'
        )
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <!-- Rounded window clip -->
    <clipPath id="window-clip">
      <rect width="{W}" height="{H}" rx="10" ry="10"/>
    </clipPath>
    <!-- Row clip paths for typewriter wipe -->
{chr(10).join(clips)}
  </defs>

  <g clip-path="url(#window-clip)">
    <!-- Terminal window background -->
    <rect width="{W}" height="{H}" fill="{BG_OUTER}"/>

    <!-- Title bar -->
    <rect width="{W}" height="{HEADER_H}" fill="{BG_INNER}"/>
    <line x1="0" y1="{HEADER_H}" x2="{W}" y2="{HEADER_H}" stroke="{BORDER}" stroke-width="1"/>

    <!-- Mac traffic light buttons -->
    <circle cx="18" cy="{HEADER_H // 2}" r="6" fill="{RED_DOT}"/>
    <circle cx="38" cy="{HEADER_H // 2}" r="6" fill="{YEL_DOT}"/>
    <circle cx="58" cy="{HEADER_H // 2}" r="6" fill="{GRN_DOT}"/>

    <!-- Window Title -->
    <text x="{W // 2}" y="{HEADER_H // 2 + 4}"
      font-family="monospace, Courier New" font-size="12" fill="{MUTED}"
      text-anchor="middle">~ sushil.ascii</text>

    <!-- Animated ASCII rows -->
{chr(10).join(text_elements)}
  </g>
</svg>'''
    return svg

def main():
    inp = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_INPUT
    inp_path = Path(inp)
    
    if not inp_path.exists():
        # If source-prepped doesn't exist yet, fall back to source-photo.jpg
        fallback = Path(__file__).parent.parent / "source-photo.jpg"
        if fallback.exists():
            inp_path = fallback
        else:
            print(f"❌ Neither {inp_path} nor source-photo.jpg found!")
            sys.exit(1)
            
    print(f"Converting {inp_path} to animated ASCII SVG...")
    rows = image_to_ascii(inp_path)
    svg = build_animated_svg(rows)
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"✅ profile-ascii.svg written successfully -> {OUTPUT}")

if __name__ == "__main__":
    main()
