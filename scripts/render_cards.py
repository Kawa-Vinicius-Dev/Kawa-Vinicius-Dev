"""data/status.json -> info-card.svg (Spring Boot startup log) + prod-status.svg (systemctl status).

Text lives here: edit and rerun. Both SVGs print line by line once (CSS keyframes, no SMIL).
"""
import json
from datetime import datetime, timedelta, timezone
from html import escape

BG, FG, DIM = "#0d1117", "#c9d1d9", "#8b949e"
GREEN, YELLOW, RED, BLUE = "#39d353", "#d29922", "#f85149", "#58a6ff"
FONT = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
BRT = timezone(timedelta(hours=-3))
STYLE = ("<style>.l{opacity:0;animation:in .35s ease-out forwards}"
         "@keyframes in{from{opacity:0;transform:translateX(-6px)}to{opacity:1;transform:none}}"
         ".p{animation:p 2s ease-in-out 1.5s infinite}@keyframes p{50%{opacity:.35}}</style>")

BANNER = r"""
  .   ____          _            __ _ _
 /\\ / ___'_ __ _ _(_)_ __  __ _ \ \ \ \
( ( )\___ | '_ | '_| | '_ \/ _` | \ \ \ \
 \\/  ___)| |_)| | | | | || (_| |  ) ) ) )
  '  |____| .__|_| |_|_| |_\__, | / / / /
 =========|_|==============|___/=/_/_/_/
"""


def t(s, color=None, extra=""):
    """Escaped tspan; nbsp keeps runs of spaces (renderers collapse plain ones)."""
    s = escape(s).replace(" ", "&#160;")
    return f'<tspan fill="{color}"{extra}>{s}</tspan>' if color else s


def svg(w, lines, fs, lh, pad, step):
    h = pad * 2 + len(lines) * lh
    out = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">', STYLE,
           f'<rect width="100%" height="100%" rx="8" fill="{BG}"/>',
           f'<g font-family="{FONT}" font-size="{fs}" fill="{FG}">']
    for i, frag in enumerate(lines):
        if frag:
            out.append(f'<text class="l" style="animation-delay:{i * step:.2f}s" x="{pad}" y="{pad + (i + 1) * lh - 5}">{frag}</text>')
    return "\n".join(out + ["</g>", "</svg>"])


def boot_log(s):
    done, total = s["trilha"]["feitos"], s["trilha"]["total"]
    n = round(20 * done / total)
    bar = t("[") + t("█" * n, GREEN) + t("░" * (20 - n), DIM) + t(f"] {done}/{total}")
    info, warn = t("INFO ", GREEN), t("WARN ", YELLOW)
    lines = [t(l, DIM) for l in BANNER.strip("\n").splitlines()]
    lines += [
        t(" :: Kawã Viana ::", GREEN, ' font-weight="bold"') + t("              (v2026.09)", DIM),
        "",
        info + t("Starting KawaApplication · Ciência da Computação"),
        info + t('Profile ativo: "backend"'),
        info + t("Stack: Java, Spring Boot, PostgreSQL, React, TS"),
        info + t("Mapped /producao → FluxoDeGestao (cliente real)"),
        info + t("Mapped /projetos → PedeAi, InventarioRFID, Cardapio"),
        info + t("Trilha Backend Java ") + bar,
        warn + t("JUnit 5, Mockito, JDBC, Docker: em treinamento"),
        info + t("Started KawaApplication in 2.3 seconds", GREEN),
        info + t("Aberto a vagas: júnior / trainee / estágio"),
        info + t("Contato: kawa.vinicius.dev@gmail.com", BLUE),
    ]
    return svg(490, lines, 12, 21, 18, 0.1)


def prod_status(s):
    checks = s.get("checks", [])
    ind = lambda k: t(f"{k:>11}: ", DIM)
    if not checks:
        dot, active = YELLOW, t("activating", YELLOW) + t(" (aguardando a primeira verificação)")
        last = t("-")
    else:
        c = checks[-1]
        ok = sum(x["up"] for x in checks)
        at = datetime.strptime(c["at"], "%Y-%m-%dT%H:%MZ").replace(tzinfo=timezone.utc).astimezone(BRT)
        first = datetime.strptime(checks[0]["at"][:10], "%Y-%m-%d").strftime("%d/%m/%Y")
        dot = GREEN if c["up"] else RED
        state = t("active (running)", GREEN, ' font-weight="bold"') if c["up"] else t("failed", RED, ' font-weight="bold"')
        active = state + t(f" · {ok}/{len(checks)} verificações diárias OK · monitorado desde {first}")
        last = t(f"{at:%d/%m %H:%M} (BRT) · HTTP {c['code'] or 'timeout'}" + (f" · {c['ms']} ms" if c["ms"] else ""))
    lines = [
        t("●", dot, ' class="p"') + t(" fluxo-de-gestao.service", FG, ' font-weight="bold"')
        + t(" - Gestão financeira p/ empresa de guincho · cliente real"),
        ind("Loaded") + t("loaded (Java · Spring Boot · PostgreSQL · React · TypeScript)"),
        ind("Active") + active,
        ind("Last check") + last,
        ind("Docs") + t("github.com/Kawa-Vinicius-Dev/gestao-guincho-demo", BLUE) + t("  (versão demo)", DIM),
    ]
    return svg(860, lines, 13, 24, 18, 0.15)


if __name__ == "__main__":
    s = json.load(open("data/status.json", encoding="utf-8"))
    open("info-card.svg", "w", encoding="utf-8").write(boot_log(s))
    open("prod-status.svg", "w", encoding="utf-8").write(prod_status(s))
    print("wrote info-card.svg, prod-status.svg")
