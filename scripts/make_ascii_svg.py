#!/usr/bin/env python3
"""
make_ascii_svg.py
Generates profile-ascii.svg — a placeholder terminal frame
that types "[ photo goes here ]" character by character.
When you supply a real headshot, replace this with a proper
ASCII art conversion using Pillow + numpy.

Usage:
  python3 scripts/make_ascii_svg.py
  (or with photo: python3 scripts/make_ascii_svg.py path/to/photo.jpg)
"""

import sys
from pathlib import Path

OUTPUT = Path(__file__).parent.parent / "profile-ascii.svg"

MONO = "JetBrains Mono, Fira Code, Consolas, monospace"
BG       = "#0d1117"
BG_INNER = "#161b22"
BORDER   = "#30363d"
GREEN    = "#39d353"
MUTED    = "#6e7681"
WHITE    = "#e6edf3"
RED_DOT  = "#ff5f57"
YEL_DOT  = "#febc2e"
GRN_DOT  = "#28c840"

W = 370
H = 320
HEADER_H = 36

# Placeholder ASCII art lines — replace with real ASCII when photo provided
PLACEHOLDER_LINES = [
    "  ╔══════════════════════════╗  ",
    "  ║                          ║  ",
    "  ║                          ║  ",
    "  ║      [ photo goes here ] ║  ",
    "  ║                          ║  ",
    "  ║   Drop your photo into   ║  ",
    "  ║   the workspace and run: ║  ",
    "  ║                          ║  ",
    "  ║  python3 scripts/        ║  ",
    "  ║    make_ascii_svg.py     ║  ",
    "  ║    path/to/photo.jpg     ║  ",
    "  ║                          ║  ",
    "  ╚══════════════════════════╝  ",
]


def char_delay(row: int, col: int, chars_per_row: int) -> str:
    """Sequential typing delay: each char appears one after another."""
    idx = row * chars_per_row + col
    return f"{idx * 18}ms"


def build_placeholder_svg() -> str:
    rows = PLACEHOLDER_LINES
    n_rows = len(rows)
    max_cols = max(len(r) for r in rows)

    content_h = H - HEADER_H
    font_size = min(content_h // (n_rows + 2), 13)
    line_h = font_size + 3
    start_y = HEADER_H + (content_h - n_rows * line_h) // 2 + font_size

    row_svgs = []
    for ri, row_text in enumerate(rows):
        y = start_y + ri * line_h
        # Animate entire row at once (simpler for placeholder)
        delay = f"{ri * 60}ms"
        row_svgs.append(
            f'<text x="{W // 2}" y="{y}" '
            f'font-family="{MONO}" font-size="{font_size}" fill="{GREEN}" '
            f'text-anchor="middle" opacity="0" '
            f'style="animation:rowFade 0.3s ease forwards;animation-delay:{delay}">'
            f'{row_text}</text>'
        )

    # Cursor blink at bottom
    cur_y = start_y + n_rows * line_h + 4
    row_svgs.append(
        f'<rect x="{W // 2 - 4}" y="{cur_y - font_size}" width="8" height="{font_size + 1}" '
        f'fill="{GREEN}" style="animation:blink 1s step-end infinite"/>'
    )

    content = "\n    ".join(row_svgs)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&amp;display=swap');
      @keyframes rowFade {{
        from {{ opacity:0; transform:translateY(4px); }}
        to   {{ opacity:1; transform:translateY(0);   }}
      }}
      @keyframes blink {{
        0%,100% {{ opacity:1; }}
        50%      {{ opacity:0; }}
      }}
    </style>
    <clipPath id="ascii-clip"><rect width="{W}" height="{H}" rx="10"/></clipPath>
  </defs>

  <g clip-path="url(#ascii-clip)">
    <!-- Background -->
    <rect width="{W}" height="{H}" fill="{BG}"/>

    <!-- Title bar -->
    <rect width="{W}" height="{HEADER_H}" fill="{BG_INNER}"/>
    <line x1="0" y1="{HEADER_H}" x2="{W}" y2="{HEADER_H}" stroke="{BORDER}" stroke-width="1"/>

    <!-- Traffic lights -->
    <circle cx="18" cy="{HEADER_H // 2}" r="5" fill="{RED_DOT}"/>
    <circle cx="36" cy="{HEADER_H // 2}" r="5" fill="{YEL_DOT}"/>
    <circle cx="54" cy="{HEADER_H // 2}" r="5" fill="{GRN_DOT}"/>

    <!-- Title -->
    <text x="{W // 2}" y="{HEADER_H // 2 + 4}"
      font-family="{MONO}" font-size="12" fill="{MUTED}" text-anchor="middle">~ profile.ascii</text>

    <!-- ASCII content -->
    {content}
  </g>
</svg>'''
    return svg


def main():
    photo_path = sys.argv[1] if len(sys.argv) > 1 else None

    if photo_path:
        # When a real photo is provided, use Pillow + numpy for ASCII conversion
        try:
            from PIL import Image
            import numpy as np

            img = Image.open(photo_path).convert("L")  # grayscale
            # Resize to fit terminal columns (aspect corrected)
            cols = 55
            rows_target = 28
            img = img.resize((cols, rows_target), Image.LANCZOS)
            arr = np.array(img)

            density = " .`:-=+*cs#%@"
            ascii_rows = []
            for row in arr:
                line = ""
                for px in row:
                    line += density[int(px / 255 * (len(density) - 1))]
                ascii_rows.append(line)

            global PLACEHOLDER_LINES
            PLACEHOLDER_LINES = ascii_rows
            print(f"🖼   Converted {photo_path} to {cols}×{rows_target} ASCII")
        except ImportError:
            print("⚠️   Pillow/numpy not installed – falling back to placeholder")
        except Exception as e:
            print(f"⚠️   Could not process photo ({e}) – falling back to placeholder")

    svg = build_placeholder_svg()
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"✅  profile-ascii.svg written → {OUTPUT}")


if __name__ == "__main__":
    main()
