"""Writes info-card.svg: neofetch-style panel that prints line by line. Edit ROWS and rerun."""
from html import escape

USER = "kawa@github"
ROWS = [
    ("Nome", "Kawã Viana"),
    ("Foco", "Backend · Java / Spring Boot"),
    ("Formação", "Ciência da Computação"),
    ("Produção", "Fluxo de Gestão (cliente real)"),
    ("Projetos", "PedeAí · RFID Android · Cardápio"),
    ("Stack", "Java, Spring, PostgreSQL, React, TS"),
    ("Estudando", "JUnit 5, Mockito, JDBC, Docker"),
    ("Agora", "Protocolo Carrasco · 247 exercícios"),
    ("Status", "aberto a júnior / trainee / estágio"),
    ("Contato", "kawa.vinicius.dev@gmail.com"),
]
W, PAD, LH, FS = 490, 22, 26, 14
BG, FG, KEY, DIM = "#0d1117", "#c9d1d9", "#39d353", "#484f58"
BLOCKS = ["#161b22", "#0e4429", "#006d32", "#26a641", "#39d353", "#58a6ff", "#d2a8ff", "#f0883e"]
STEP = 0.12  # seconds between lines

lines = [  # (svg fragment, y)
    (f'<tspan fill="{KEY}" font-weight="bold">{USER}</tspan>', 0),
    (f'<tspan fill="{DIM}">{"-" * len(USER)}</tspan>', 1),
]
for i, (k, v) in enumerate(ROWS):
    lines.append((f'<tspan fill="{KEY}" font-weight="bold">{escape(k)}</tspan><tspan fill="{DIM}">: </tspan>{escape(v)}', i + 2))

H = PAD * 2 + (len(lines) + 1) * LH + 18
out = [
    f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">',
    "<style>.l{opacity:0;animation:in .4s ease-out forwards}"
    "@keyframes in{from{opacity:0;transform:translateX(-8px)}to{opacity:1;transform:none}}</style>",
    f'<rect width="100%" height="100%" rx="8" fill="{BG}"/>',
    f'<g font-family="ui-monospace,SFMono-Regular,Menlo,Consolas,monospace" font-size="{FS}" fill="{FG}">',
]
for frag, n in lines:
    out.append(f'<text class="l" style="animation-delay:{n * STEP:.2f}s" x="{PAD}" y="{PAD + (n + 1) * LH - 8}">{frag}</text>')
by, n = PAD + (len(lines) + 0.6) * LH, len(lines)
out.append(f'<g class="l" style="animation-delay:{n * STEP:.2f}s">')
out += [f'<rect x="{PAD + i * 26}" y="{by:.0f}" width="22" height="16" rx="3" fill="{c}"/>' for i, c in enumerate(BLOCKS)]
out += ["</g>", "</g>", "</svg>"]

open("info-card.svg", "w", encoding="utf-8").write("\n".join(out))
print("wrote info-card.svg")
