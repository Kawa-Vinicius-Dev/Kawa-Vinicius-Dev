"""data/contributions.json -> contrib-heatmap.svg: 53x7 grid that slides in diagonally once."""
import json
from datetime import date

PALETTE = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353"]  # GitHub levels 0..4
BG, FG, DIM = "#0d1117", "#c9d1d9", "#8b949e"
MONTHS = "jan fev mar abr mai jun jul ago set out nov dez".split()
CELL, GAP, LEFT, TOP, PAD = 12, 3, 34, 38, 16
STEP = 0.012  # seconds per diagonal

d = json.load(open("data/contributions.json", encoding="utf-8"))
days = d["days"]
first = date.fromisoformat(days[0]["date"])
offset = (first.weekday() + 1) % 7  # Sunday = row 0, like GitHub
W = 860
out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} 200" width="{W}" height="200">',
    "<style>.c{opacity:0;animation:in .45s ease-out forwards}"
    "@keyframes in{from{opacity:0;transform:translateY(-6px)}to{opacity:1;transform:none}}"
    f"text{{font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:11px;fill:{DIM}}}</style>",
    f'<rect width="100%" height="100%" rx="8" fill="{BG}"/>',
]
for r, name in ((1, "seg"), (3, "qua"), (5, "sex")):
    out.append(f'<text x="{PAD}" y="{TOP + r * (CELL + GAP) + 10}">{name}</text>')

last_month = None
for i, day in enumerate(days):
    dt = date.fromisoformat(day["date"])
    col, row = divmod(i + offset, 7)
    x, y = PAD + LEFT + col * (CELL + GAP), TOP + row * (CELL + GAP)
    if row == 0 and dt.month != last_month and dt.day <= 7:
        out.append(f'<text x="{x}" y="{TOP - 8}">{MONTHS[dt.month - 1]}</text>')
        last_month = dt.month
    out.append(f'<rect class="c" style="animation-delay:{(col + row) * STEP:.3f}s" x="{x}" y="{y}" '
               f'width="{CELL}" height="{CELL}" rx="2.5" fill="{PALETTE[day["level"]]}"/>')

fy = TOP + 7 * (CELL + GAP) + 22
b = d["best_day"]
bd = date.fromisoformat(b["date"]).strftime("%d/%m") if b["date"] else "-"
out.append(f'<text x="{PAD + LEFT}" y="{fy}" style="fill:{FG}">{d["total"]:,} contribuições no último ano'.replace(",", ".")
           + f'<tspan style="fill:{DIM}">  ·  sequência atual {d["current_streak"]}d  ·  maior {d["longest_streak"]}d'
             f'  ·  melhor dia {b["count"]} ({bd})</tspan></text>')
lx = W - PAD - 5 * (CELL + GAP) - 36
out.append(f'<text x="{lx - 44}" y="{fy}">menos</text>')
out += [f'<rect x="{lx + i * (CELL + GAP)}" y="{fy - 10}" width="{CELL}" height="{CELL}" rx="2.5" fill="{c}"/>'
        for i, c in enumerate(PALETTE)]
out.append(f'<text x="{lx + 5 * (CELL + GAP) + 4}" y="{fy}">mais</text>')
out.append("</svg>")

open("contrib-heatmap.svg", "w", encoding="utf-8").write("\n".join(out))
print("wrote contrib-heatmap.svg")
