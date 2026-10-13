#!/usr/bin/env python3
"""
render_heatmap_svg.py
Reads data/contributions.json and renders contrib-heatmap.svg —
a 53-week × 7-day GitHub-style contribution graph with:
  • GitHub green palette (#161b22 → #69f0a0)
  • Diagonal box-reveal SMIL animation
  • Stats bar (total / current streak / longest streak)
"""

import json
import sys
from pathlib import Path

DATA_FILE = Path(__file__).parent.parent / "data" / "contributions.json"
OUTPUT    = Path(__file__).parent.parent / "contrib-heatmap.svg"

MONO = "JetBrains Mono, Fira Code, Consolas, monospace"

# Color palette: level 0..4
LEVELS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]

# Highlight accent for stats bar
ACCENT = "#39d353"

# Layout
CELL     = 11   # cell size px
GAP      = 2    # gap between cells
COL_W    = CELL + GAP
ROW_H    = CELL + GAP

MARGIN_LEFT  = 28   # space for day labels
MARGIN_TOP   = 24   # space for month labels
MARGIN_BOTTOM = 54  # space for legend + stats

MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
DAYS   = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"]

BG      = "#0d1117"
BORDER  = "#21262d"
TEXT_DIM = "#6e7681"
TEXT_MED = "#8b949e"
TEXT_LT  = "#e6edf3"
GREEN_DIM = "#0e4429"


def load_data() -> dict:
    if not DATA_FILE.exists():
        print(f"⚠️   {DATA_FILE} not found – run fetch_contributions.py first", file=sys.stderr)
        sys.exit(1)
    return json.loads(DATA_FILE.read_text())


def build_svg(data: dict) -> str:
    weeks  = data.get("weeks", [])
    total  = data.get("total", 0)
    c_str  = data.get("current_streak", 0)
    l_str  = data.get("longest_streak", 0)
    n_cols = len(weeks)

    W = MARGIN_LEFT + n_cols * COL_W + 10
    H = MARGIN_TOP  + 7 * ROW_H + MARGIN_BOTTOM

    cells_svg  = []
    month_seen = {}

    for ci, week in enumerate(weeks):
        x = MARGIN_LEFT + ci * COL_W
        for ri, day in enumerate(week):
            y = MARGIN_TOP + ri * ROW_H
            level  = day.get("level", 0)
            count  = day.get("count", 0)
            date   = day.get("date", "")
            color  = LEVELS[min(level, 4)]

            # Diagonal reveal: delay = (col + row) * step_ms
            diag   = ci + ri
            begin  = f"{diag * 18}ms"

            tip = f"{count} contribution{'s' if count != 1 else ''} on {date}"

            cells_svg.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2" ry="2" '
                f'fill="{color}" data-date="{date}" data-count="{count}">'
                f'  <title>{tip}</title>'
                f'  <animate attributeName="opacity" from="0" to="1" '
                f'    dur="0.3s" begin="{begin}" fill="freeze"/>'
                f'</rect>'
            )

            # Track first occurrence of each month for label placement
            if date and len(date) == 10:
                month_num = int(date[5:7]) - 1
                if month_num not in month_seen:
                    month_seen[month_num] = x

    # Month labels
    month_labels = []
    for m, lx in month_seen.items():
        month_labels.append(
            f'<text x="{lx}" y="{MARGIN_TOP - 6}" '
            f'font-family="{MONO}" font-size="10" fill="{TEXT_DIM}">{MONTHS[m]}</text>'
        )

    # Day labels (Mon, Wed, Fri only — standard GitHub style)
    day_labels = []
    for di in [1, 3, 5]:
        dy = MARGIN_TOP + di * ROW_H + CELL - 1
        day_labels.append(
            f'<text x="{MARGIN_LEFT - 4}" y="{dy}" '
            f'font-family="{MONO}" font-size="9" fill="{TEXT_DIM}" text-anchor="end">{DAYS[di]}</text>'
        )

    # Legend
    legend_y = H - 20
    legend_label_x = MARGIN_LEFT
    legend_items = []
    legend_items.append(
        f'<text x="{legend_label_x}" y="{legend_y + CELL - 1}" '
        f'font-family="{MONO}" font-size="10" fill="{TEXT_DIM}">Less</text>'
    )
    for li, lc in enumerate(LEVELS):
        lx = legend_label_x + 32 + li * (CELL + 3)
        legend_items.append(
            f'<rect x="{lx}" y="{legend_y}" width="{CELL}" height="{CELL}" rx="2" fill="{lc}"/>'
        )
    legend_items.append(
        f'<text x="{legend_label_x + 32 + len(LEVELS) * (CELL + 3) + 4}" y="{legend_y + CELL - 1}" '
        f'font-family="{MONO}" font-size="10" fill="{TEXT_DIM}">More</text>'
    )

    # Stats bar
    stats_y = H - 42
    stats = [
        (f"{total}", "Contributions this year"),
        (f"{c_str}", "Current streak"),
        (f"{l_str}", "Longest streak"),
    ]
    stats_svg = []
    stat_x = MARGIN_LEFT
    for val, label in stats:
        stats_svg.append(
            f'<text x="{stat_x}" y="{stats_y}" '
            f'font-family="{MONO}" font-size="13" font-weight="700" fill="{ACCENT}">{val}</text>'
        )
        # Measure approx width: digit count * 8 + gap
        val_w = len(val) * 8 + 4
        stats_svg.append(
            f'<text x="{stat_x + val_w}" y="{stats_y}" '
            f'font-family="{MONO}" font-size="11" fill="{TEXT_MED}"> {label}</text>'
        )
        stat_x += max(len(val) * 8 + len(label) * 7 + 30, 160)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
  <defs>
    <style>
      @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&amp;display=swap');
    </style>
    <clipPath id="hm-clip"><rect width="{W}" height="{H}" rx="10"/></clipPath>
  </defs>

  <g clip-path="url(#hm-clip)">
    <rect width="{W}" height="{H}" fill="{BG}"/>

    <!-- Month labels -->
    {"".join(month_labels)}

    <!-- Day labels -->
    {"".join(day_labels)}

    <!-- Cells (diagonal reveal) -->
    {"".join(cells_svg)}

    <!-- Stats bar -->
    {"".join(stats_svg)}

    <!-- Legend -->
    {"".join(legend_items)}
  </g>
</svg>'''
    return svg


def main():
    data = load_data()
    svg = build_svg(data)
    OUTPUT.write_text(svg, encoding="utf-8")
    print(f"✅  contrib-heatmap.svg written ({len(data.get('weeks', []))} weeks) → {OUTPUT}")


if __name__ == "__main__":
    main()
