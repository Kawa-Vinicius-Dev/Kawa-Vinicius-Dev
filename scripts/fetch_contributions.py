"""Scrape the public contribution calendar (no token) -> data/contributions.json.

Fails loudly if GitHub changes the markup, so the workflow errors out and the
last committed SVG stays on the profile instead of an empty graph.
"""
import json
import re
from datetime import date, timedelta

import requests
from bs4 import BeautifulSoup

USER = "Kawa-Vinicius-Dev"


def stats(days):
    """days: list of {date, count} sorted by date. Today may still be 0, so the current streak may end yesterday."""
    counts = [d["count"] for d in days]
    longest = run = 0
    for c in counts:
        run = run + 1 if c else 0
        longest = max(longest, run)
    i = len(counts) - 1
    if i >= 0 and counts[i] == 0:
        i -= 1
    current = 0
    while i >= 0 and counts[i]:
        current, i = current + 1, i - 1
    best = max(days, key=lambda d: d["count"], default={"date": None, "count": 0})
    return {"total": sum(counts), "current_streak": current, "longest_streak": longest,
            "best_day": {"date": best["date"], "count": best["count"]}}


def fetch():
    html = requests.get(f"https://github.com/users/{USER}/contributions", timeout=30)
    html.raise_for_status()
    soup = BeautifulSoup(html.text, "html.parser")
    tips = {t["for"]: t.get_text() for t in soup.find_all("tool-tip") if t.get("for")}
    days = []
    for td in soup.select("td.ContributionCalendar-day[data-date]"):
        m = re.match(r"(\d[\d,]*) contribution", tips.get(td.get("id"), ""))
        days.append({"date": td["data-date"], "level": int(td["data-level"]),
                     "count": int(m.group(1).replace(",", "")) if m else 0})
    if len(days) < 300:
        raise SystemExit(f"parsed only {len(days)} days - GitHub markup changed?")
    days.sort(key=lambda d: d["date"])
    return {"user": USER, "days": days, **stats(days)}


if __name__ == "__main__":
    # self-check for the streak logic
    d0 = date(2026, 1, 1)
    mk = lambda cs: [{"date": str(d0 + timedelta(i)), "count": c} for i, c in enumerate(cs)]
    assert stats(mk([1, 1, 0, 2, 3, 0]))["current_streak"] == 2  # today empty -> count from yesterday
    assert stats(mk([1, 1, 1, 0, 2, 3]))["current_streak"] == 2
    assert stats(mk([1, 1, 1, 0, 2, 3]))["longest_streak"] == 3
    assert stats(mk([0, 5, 0]))["best_day"] == {"date": "2026-01-02", "count": 5}

    data = fetch()
    with open("data/contributions.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=1)
    print(f"{len(data['days'])} days, {data['total']} contributions")
