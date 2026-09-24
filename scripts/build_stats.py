"""Rebuild the live cards in assets/generated/ from public GitHub data.

Runs daily in .github/workflows/stats.yml. Standard library only.
"""
import datetime as dt
import json
import math
import os
import re
import urllib.request
from xml.sax.saxutils import escape

USER = os.environ.get("GH_USER", "FahadNafeesAhmed")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "assets", "generated")

SANS = "'Segoe UI',-apple-system,BlinkMacSystemFont,'Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "'JetBrains Mono','Cascadia Code','SFMono-Regular',Consolas,Menlo,'Liberation Mono',monospace"
C = dict(bg="#0A0E16", bg2="#0E1524", border="#1d2940", text="#E6EDF6", muted="#8C9BB5", dim="#4A5872",
         faint="#243049", mint="#5EEAD4", cyan="#38BDF8", violet="#A78BFA", pink="#F472B6", amber="#FBBF24",
         green="#4ADE80")
PALETTE = [C["mint"], C["cyan"], C["violet"], C["pink"], C["amber"], C["green"]]
LANG_MAP = {"Jupyter Notebook": "Python"}
LANG_SKIP = {"HTML", "CSS", "SCSS", "Shell", "Dockerfile", "Makefile", "PowerShell", "Batchfile", "Procfile"}


def get(url, api=True):
    req = urllib.request.Request(url, headers={"User-Agent": f"{USER}-profile-stats"})
    if api:
        req.add_header("Accept", "application/vnd.github+json")
        if TOKEN:
            req.add_header("Authorization", f"Bearer {TOKEN}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode("utf-8")


def contributions():
    """Daily counts for the last year, scraped from the public contribution calendar."""
    html = get(f"https://github.com/users/{USER}/contributions", api=False)
    ids = re.findall(r'data-date="(\d{4}-\d\d-\d\d)" id="(contribution-day-component-\d+-\d+)"', html)
    tips = dict(re.findall(r'for="(contribution-day-component-\d+-\d+)"[^>]*>([^<]*)</tool-tip>', html))
    days = []
    for date, cid in ids:
        m = re.match(r"([\d,]+) contribution", tips.get(cid, ""))
        days.append((dt.date.fromisoformat(date), int(m.group(1).replace(",", "")) if m else 0))
    if len(days) < 300:
        raise SystemExit(f"contribution calendar parse failed ({len(days)} days); keeping old cards")
    return sorted(days)


def streaks(days):
    longest = run = 0
    for _, n in days:
        run = run + 1 if n else 0
        longest = max(longest, run)
    cur, i = 0, len(days) - 1
    if days[i][1] == 0:  # today may not have started yet
        i -= 1
    while i >= 0 and days[i][1]:
        cur, i = cur + 1, i - 1
    return cur, longest


def repos_and_languages():
    repos = json.loads(get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner"))
    own = [r for r in repos if not r["fork"] and r["name"].lower() != USER.lower()]
    share = {}
    for r in own:
        langs = json.loads(get(r["languages_url"]))
        code = {}
        for k, v in langs.items():
            k = LANG_MAP.get(k, k)
            if k not in LANG_SKIP:
                code[k] = code.get(k, 0) + v
        total = sum(code.values())
        for k, v in code.items():  # every project counts once, split by its bytes
            share[k] = share.get(k, 0) + v / total
    stars = sum(r["stargazers_count"] for r in own)
    return len(own), stars, sorted(share.items(), key=lambda kv: -kv[1])


def svg(w, h, body, css, title):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" fill="none" role="img">'
            f"<title>{escape(title)}</title><style>text{{font-family:{SANS}}}.m{{font-family:{MONO}}}{css}"
            "@media (prefers-reduced-motion: reduce){*{animation:none!important}}</style>"
            f'<defs><linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="{C["bg2"]}"/>'
            f'<stop offset="1" stop-color="{C["bg"]}"/></linearGradient></defs>'
            f'<rect x=".5" y=".5" width="{w-1}" height="{h-1}" rx="16" fill="url(#bg)" stroke="{C["border"]}"/>{body}</svg>')


def head(label, title):
    return (f'<text class="m" x="24" y="36" font-size="11.5" fill="{C["muted"]}" letter-spacing="1">{label}</text>'
            f'<text x="24" y="62" font-size="19" font-weight="700" fill="{C["text"]}">{escape(title)}</text>')


def stats_card(days, n_repos, stars, today):
    total = sum(n for _, n in days)
    cur, longest = streaks(days)
    active = sum(1 for _, n in days if n)
    weeks = [sum(n for _, n in days[i:i + 7]) for i in range(0, len(days), 7)]
    top = max(weeks) or 1
    x0, x1, y0, y1 = 24, 416, 172, 222
    pts = [(x0 + (x1 - x0) * i / (len(weeks) - 1), y1 - (y1 - y0) * v / top) for i, v in enumerate(weeks)]
    line = "M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in pts)
    area = line + f" L{x1} {y1} L{x0} {y1} Z"
    rows = [("current streak", f"{cur} day{'s' * (cur != 1)}", C["mint"]),
            ("longest streak", f"{longest} days", C["cyan"]),
            ("active days", f"{active}", C["violet"])]
    body = head("// GITHUB", "The last 12 months")
    body += (f'<text x="24" y="118" font-size="46" font-weight="800" fill="url(#g)" class="up">{total:,}</text>'
             f'<text x="26" y="140" font-size="12.5" fill="{C["muted"]}">contributions</text>'
             f'<defs><linearGradient id="g" x1="0" x2="1"><stop offset="0" stop-color="{C["mint"]}"/><stop offset="1" stop-color="{C["cyan"]}"/></linearGradient>'
             f'<linearGradient id="a" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="{C["mint"]}" stop-opacity=".35"/>'
             f'<stop offset="1" stop-color="{C["mint"]}" stop-opacity="0"/></linearGradient></defs>')
    for i, (lab, val, col) in enumerate(rows):
        y = 92 + i * 24
        body += (f'<text x="236" y="{y}" font-size="12.5" fill="{C["muted"]}">{lab}</text>'
                 f'<text class="m up" x="416" y="{y}" font-size="13" font-weight="700" fill="{col}" text-anchor="end" '
                 f'style="animation-delay:{.2+i*.12:.2f}s">{val}</text>')
    body += (f'<path d="{area}" fill="url(#a)"/><path class="ln" d="{line}" stroke="{C["mint"]}" stroke-width="1.8" stroke-linejoin="round"/>'
             f'<text class="m" x="{x0}" y="{y1+16}" font-size="9.5" fill="{C["dim"]}">{days[0][0]:%b %Y}</text>'
             f'<text class="m" x="{x1}" y="{y1+16}" font-size="9.5" fill="{C["dim"]}" text-anchor="end">weekly · {today:%b %Y}</text>'
             f'<text class="m" x="416" y="36" font-size="10" fill="{C["dim"]}" text-anchor="end">{n_repos} projects · {stars} ★</text>')
    css = (".up{opacity:0;animation:up .6s ease-out forwards}@keyframes up{from{opacity:0;transform:translateY(6px)}to{opacity:1;transform:none}}"
           ".ln{stroke-dasharray:1400;stroke-dashoffset:1400;animation:dr 2.2s ease-out forwards}@keyframes dr{to{stroke-dashoffset:0}}")
    return svg(440, 250, body, css, f"{total} contributions in the last year")


def languages_card(share):
    top = share[:6]
    rest = sum(v for _, v in share[6:])
    if rest:
        top.append(("Other", rest))
    total = sum(v for _, v in top)
    cx, cy, r, sw = 110, 152, 58, 20
    circ = 2 * math.pi * r
    body = head("// LANGUAGES", "Share of my projects")
    off = 0.0
    for i, (name, v) in enumerate(top):
        frac = v / total
        col = PALETTE[i] if name != "Other" else C["dim"]
        body += (f'<circle class="seg" cx="{cx}" cy="{cy}" r="{r}" stroke="{col}" stroke-width="{sw}" '
                 f'stroke-dasharray="{max(frac*circ-2, .5):.2f} {circ:.2f}" stroke-dashoffset="{-off:.2f}" '
                 f'transform="rotate(-90 {cx} {cy})" style="animation-delay:{i*.1:.1f}s"/>')
        off += frac * circ
        y = 96 + i * 22
        body += (f'<g class="up" style="animation-delay:{.2+i*.08:.2f}s"><circle cx="228" cy="{y-4}" r="4.5" fill="{col}"/>'
                 f'<text x="242" y="{y}" font-size="13" fill="{C["text"]}">{escape(name)}</text>'
                 f'<text class="m" x="416" y="{y}" font-size="12.5" fill="{C["muted"]}" text-anchor="end">{100*frac:.1f}%</text></g>')
    body += (f'<text x="{cx}" y="{cy+2}" font-size="22" font-weight="800" fill="{C["text"]}" text-anchor="middle">{len(share)}</text>'
             f'<text x="{cx}" y="{cy+18}" font-size="10.5" fill="{C["muted"]}" text-anchor="middle">languages</text>'
             f'<text class="m" x="24" y="236" font-size="9.5" fill="{C["dim"]}">each project counts once, split by its code</text>')
    css = (".seg{opacity:0;animation:fi .8s ease-out forwards}@keyframes fi{to{opacity:1}}"
           ".up{opacity:0;animation:up .5s ease-out forwards}@keyframes up{from{opacity:0;transform:translateX(-4px)}to{opacity:1;transform:none}}")
    return svg(440, 250, body, css, "Languages across my projects")


def shade(hex_color, k):
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return f"#{int(r*k):02x}{int(g*k):02x}{int(b*k):02x}"


def activity_card(days):
    W, H = 900, 290
    first = days[0][0] - dt.timedelta(days=(days[0][0].weekday() + 1) % 7)
    cw, s, dx, dy, dep = 14.6, 10.6, 5.0, 7.0, 0.72
    X0, Y0 = 36, 200
    mx = max(n for _, n in days) or 1
    nz = sorted(n for _, n in days if n)
    q = [nz[int(len(nz) * f)] for f in (.25, .5, .75)] if nz else [1, 2, 3]
    tops = ["#172238", "#0f5e55", "#149c88", "#2dd4bf", "#a7f3e4"]
    cols = {}
    for day, n in days:
        w, d = (day - first).days // 7, (day.weekday() + 1) % 7
        cols.setdefault(w, []).append((d, n, day))
    body = head("// CONTRIBUTIONS", "A year of building, in 3D")
    busiest = max(days, key=lambda t: t[1])
    body += (f'<text class="m" x="{W-24}" y="36" font-size="11" fill="{C["muted"]}" text-anchor="end">'
             f'{sum(n for _, n in days):,} contributions · busiest day {busiest[0]:%b %d} ({busiest[1]})</text>')
    lx = W - 24 - 28 - 5 * 16
    body += f'<text class="m" x="{lx-8}" y="60" font-size="10" fill="{C["dim"]}" text-anchor="end">less</text>'
    for i, c in enumerate(tops):
        body += f'<rect x="{lx+i*16}" y="51" width="11" height="11" rx="2" fill="{c}"/>'
    body += f'<text class="m" x="{lx+5*16+2}" y="60" font-size="10" fill="{C["dim"]}">more</text>'
    ddx, ddy = dx * dep, dy * dep
    for w in sorted(cols):
        g = ""
        for d, n, day in sorted(cols[w]):
            x, y = X0 + w * cw + (6 - d) * dx, Y0 + d * dy
            lvl = 0 if n == 0 else 1 + sum(n > t for t in q)
            h = 0 if n == 0 else 4 + 86 * math.sqrt(n / mx)
            top = tops[lvl]
            if h:
                g += (f'<path d="M{x:.1f} {y:.1f}h{s}v{-h:.1f}h{-s}z" fill="{shade(top, .62)}"/>'
                      f'<path d="M{x+s:.1f} {y:.1f}l{ddx:.1f} {-ddy:.1f}v{-h:.1f}l{-ddx:.1f} {ddy:.1f}z" fill="{shade(top, .42)}"/>')
            g += (f'<path d="M{x:.1f} {y-h:.1f}h{s}l{ddx:.1f} {-ddy:.1f}h{-s}z" fill="{top}"><title>{n} on {day:%b %d}</title></path>')
        body += f'<g class="c" style="animation-delay:{w*.018:.3f}s">{g}</g>'
    seen = set()
    for w in sorted(cols):
        day = min(t[2] for t in cols[w])
        if day.day <= 7 and day.month not in seen and w > 0:
            seen.add(day.month)
            body += (f'<text class="m" x="{X0 + w*cw:.1f}" y="{Y0 + 6*dy + 22}" font-size="10" '
                     f'fill="{C["dim"]}">{day:%b}</text>')
    css = (".c{transform-box:fill-box;transform-origin:50% 100%;transform:scaleY(0);animation:rise .9s cubic-bezier(.2,.8,.2,1) forwards}"
           "@keyframes rise{to{transform:scaleY(1)}}")
    return svg(W, H, body, css, "Contribution skyline for the last year")


def main():
    os.makedirs(OUT, exist_ok=True)
    today = dt.date.today()
    days = contributions()
    n_repos, stars, share = repos_and_languages()
    cards = {"stats.svg": stats_card(days, n_repos, stars, today),
             "languages.svg": languages_card(share),
             "activity.svg": activity_card(days)}
    for name, content in cards.items():
        with open(os.path.join(OUT, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        print(f"wrote {name} ({len(content)/1024:.1f} KB)")


if __name__ == "__main__":
    main()
