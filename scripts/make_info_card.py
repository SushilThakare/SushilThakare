#!/usr/bin/env python3
"""
make_info_card.py
Generates info-card.svg – a Neofetch-style terminal specs card
with staggered CSS slide+fade animations for SushilThakare's profile.
"""

from pathlib import Path

OUTPUT = Path(__file__).parent.parent / "info-card.svg"

# ── Profile data ────────────────────────────────────────────────────────────
FIELDS = [
    ("OS",         "macOS Sequoia 15.3"),
    ("Host",       "github.com/SushilThakare"),
    ("Shell",      "zsh + oh-my-zsh"),
    ("Role",       "Full Stack Software Engineer"),
    ("Stack",      "MERN · TypeScript · Python"),
    ("Cloud",      "GCP · Docker · Nginx"),
    ("Learning",   "ML Algorithms · LLM APIs"),
    ("Open to",    "SWE Roles · AI/ML Integrations"),
    ("Email",      "sushil.thakare.work@gmail.com"),
    ("LinkedIn",   "linkedin.com/in/sushilthakare"),
]

# ── Layout constants ─────────────────────────────────────────────────────────
W, H           = 490, 340
PAD_X, PAD_Y  = 22, 22
LINE_H         = 24
HEADER_H       = 42    # top bar height

# Mono font stack
MONO = "JetBrains Mono, Fira Code, Consolas, monospace"

# Colors (GitHub dark palette)
BG_OUTER   = "#0d1117"
BG_INNER   = "#161b22"
BORDER     = "#30363d"
CYAN       = "#79c0ff"
GREEN      = "#56d364"
PURPLE     = "#bc8cff"
YELLOW     = "#e3b341"
WHITE      = "#e6edf3"
MUTED      = "#6e7681"
RED_DOT    = "#ff5f57"
YEL_DOT    = "#febc2e"
GRN_DOT    = "#28c840"


def delay(i: int) -> str:
    """Stagger delay: 0.15s per line after a 0.3s base."""
    return f"{0.3 + i * 0.15:.2f}s"


def build_svg() -> str:
    lines_svg = []

    # Username banner at top of card
    banner_y = HEADER_H + PAD_Y + 6
    lines_svg.append(
        f'<text x="{PAD_X}" y="{banner_y}" '
        f'font-family="{MONO}" font-size="13" font-weight="700" fill="{GREEN}" '
        f'opacity="0" style="animation:fadeSlide 0.5s ease forwards;animation-delay:0.1s">'
        f'sushil@github</text>'
    )
    lines_svg.append(
        f'<text x="{PAD_X + 118}" y="{banner_y}" '
        f'font-family="{MONO}" font-size="13" fill="{WHITE}" '
        f'opacity="0" style="animation:fadeSlide 0.5s ease forwards;animation-delay:0.1s">~</text>'
    )

    # Separator line
    sep_y = banner_y + 10
    lines_svg.append(
        f'<line x1="{PAD_X}" y1="{sep_y}" x2="{W - PAD_X}" y2="{sep_y}" '
        f'stroke="{BORDER}" stroke-width="1" opacity="0.6"/>'
    )

    # Field rows
    row_start_y = sep_y + LINE_H
    for i, (label, value) in enumerate(FIELDS):
        y = row_start_y + i * LINE_H
        d = delay(i)

        # Label (cyan)
        lines_svg.append(
            f'<text x="{PAD_X}" y="{y}" '
            f'font-family="{MONO}" font-size="12" font-weight="700" fill="{CYAN}" '
            f'opacity="0" style="animation:fadeSlide 0.45s ease forwards;animation-delay:{d}">'
            f'{label}</text>'
        )
        # Separator colon (purple)
        label_w = max(len(label) * 7.5, 65)
        colon_x = PAD_X + label_w
        lines_svg.append(
            f'<text x="{colon_x}" y="{y}" '
            f'font-family="{MONO}" font-size="12" fill="{PURPLE}" '
            f'opacity="0" style="animation:fadeSlide 0.45s ease forwards;animation-delay:{d}">: </text>'
        )
        # Value (white / yellow for special fields)
        val_color = YELLOW if label in ("Open to", "Learning") else WHITE
        lines_svg.append(
            f'<text x="{colon_x + 14}" y="{y}" '
            f'font-family="{MONO}" font-size="12" fill="{val_color}" '
            f'opacity="0" style="animation:fadeSlide 0.45s ease forwards;animation-delay:{d}">'
            f'{value}</text>'
        )

    # Prompt cursor at the bottom
    prompt_y = row_start_y + len(FIELDS) * LINE_H + 6
    lines_svg.append(
        f'<text x="{PAD_X}" y="{prompt_y}" '
        f'font-family="{MONO}" font-size="12" fill="{GREEN}" '
        f'opacity="0" style="animation:fadeSlide 0.45s ease forwards;animation-delay:{delay(len(FIELDS))}">$ </text>'
    )
    lines_svg.append(
        f'<rect x="{PAD_X + 16}" y="{prompt_y - 12}" width="8" height="13" fill="{GREEN}" '
        f'opacity="0" style="animation:blink 1s step-end infinite,fadeSlide 0.45s ease forwards;animation-delay:{delay(len(FIELDS))},0s"/>'
    )

    content = "\n    ".join(lines_svg)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&amp;display=swap');
      @keyframes fadeSlide {{
        from {{ opacity:0; transform:translateX(-6px); }}
        to   {{ opacity:1; transform:translateX(0);   }}
      }}
      @keyframes blink {{
        0%,100% {{ opacity:1; }}
        50%      {{ opacity:0; }}
      }}
    </style>
    <!-- Rounded clip -->
    <clipPath id="card-clip">
      <rect width="{W}" height="{H}" rx="10" ry="10"/>
    </clipPath>
  </defs>

  <g clip-path="url(#card-clip)">
    <!-- Outer background -->
    <rect width="{W}" height="{H}" fill="{BG_OUTER}"/>

    <!-- Title bar -->
    <rect width="{W}" height="{HEADER_H}" fill="{BG_INNER}"/>
    <line x1="0" y1="{HEADER_H}" x2="{W}" y2="{HEADER_H}" stroke="{BORDER}" stroke-width="1"/>

    <!-- Traffic-light dots -->
    <circle cx="18" cy="{HEADER_H // 2}" r="6" fill="{RED_DOT}"/>
    <circle cx="38" cy="{HEADER_H // 2}" r="6" fill="{YEL_DOT}"/>
    <circle cx="58" cy="{HEADER_H // 2}" r="6" fill="{GRN_DOT}"/>

    <!-- Title text -->
    <text x="{W // 2}" y="{HEADER_H // 2 + 5}"
      font-family="{MONO}" font-size="13" fill="{MUTED}"
      text-anchor="middle">~ neofetch</text>

    <!-- Card content -->
    {content}
  </g>
</svg>'''
    return svg


def main():
    svg = build_svg()
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"✅  info-card.svg written → {OUTPUT}")


if __name__ == "__main__":
    main()
