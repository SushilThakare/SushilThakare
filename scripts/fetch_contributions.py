#!/usr/bin/env python3
"""
fetch_contributions.py
Scrapes SushilThakare's public GitHub contribution heatmap,
calculates streaks + yearly total, and saves to data/contributions.json
"""

import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "SushilThakare"
OUTPUT = Path(__file__).parent.parent / "data" / "contributions.json"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def fetch_svg_data(username: str) -> str:
    url = f"https://github.com/users/{username}/contributions"
    resp = requests.get(url, headers=HEADERS, timeout=15)
    resp.raise_for_status()
    return resp.text


def parse_contributions(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    days = {}

    # GitHub renders td elements with data-date and data-level attributes
    for td in soup.find_all("td", attrs={"data-date": True}):
        date_str = td.get("data-date", "")
        level = int(td.get("data-level", 0))
        # Try to extract the count from the tooltip text
        title = td.get("aria-label", "")
        count = 0
        m = re.search(r"(\d+)\s+contribution", title)
        if m:
            count = int(m.group(1))
        if date_str:
            days[date_str] = {"level": level, "count": count}

    # Build ordered list sorted by date
    sorted_days = sorted(days.items())

    # Yearly total
    total = sum(v["count"] for _, v in sorted_days)

    # Current streak
    today = datetime.today().date()
    current_streak = 0
    check = today
    while True:
        ds = check.strftime("%Y-%m-%d")
        if ds in days and days[ds]["count"] > 0:
            current_streak += 1
            check -= timedelta(days=1)
        else:
            break

    # Longest streak
    longest_streak = 0
    running = 0
    for ds, v in sorted_days:
        if v["count"] > 0:
            running += 1
            longest_streak = max(longest_streak, running)
        else:
            running = 0

    # Build the 53-week grid (week = Sun..Sat columns)
    # Find the start date: first Sunday on or before the first day
    if sorted_days:
        first_date = datetime.strptime(sorted_days[0][0], "%Y-%m-%d").date()
        last_date = datetime.strptime(sorted_days[-1][0], "%Y-%m-%d").date()
    else:
        last_date = today
        first_date = today - timedelta(weeks=52)

    # Snap first_date back to Sunday
    start = first_date - timedelta(days=first_date.weekday() + 1 if first_date.weekday() != 6 else 0)

    weeks = []
    cur = start
    while cur <= last_date + timedelta(days=6):
        week = []
        for _ in range(7):
            ds = cur.strftime("%Y-%m-%d")
            week.append({"date": ds, "level": days.get(ds, {}).get("level", 0),
                         "count": days.get(ds, {}).get("count", 0)})
            cur += timedelta(days=1)
        weeks.append(week)
        if len(weeks) >= 53:
            break

    result = {
        "generated": datetime.now(timezone.utc).isoformat(),
        "username": USERNAME,
        "total": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "weeks": weeks,
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(result, indent=2))
    print(f"✅  Saved {len(weeks)} weeks, {total} total contributions → {OUTPUT}")
    return result


def main():
    print(f"🔍  Fetching contributions for @{USERNAME} …")
    try:
        html = fetch_svg_data(USERNAME)
        parse_contributions(html)
    except Exception as exc:
        print(f"❌  Error: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
