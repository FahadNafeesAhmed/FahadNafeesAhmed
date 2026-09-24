"""Generate static profile SVGs from public GitHub data. Standard library only."""

import datetime as dt
import json
import math
import os
from collections import defaultdict
from html.parser import HTMLParser
from pathlib import Path
import re
import urllib.request
from xml.sax.saxutils import escape

USER = os.environ.get("GH_USER", "FahadNafeesAhmed")
TOKEN = os.environ.get("GITHUB_TOKEN", "")
ASSETS = Path(__file__).resolve().parents[1] / "assets"


def get(url, api=True):
    headers = {"User-Agent": f"{USER}-profile-stats"}
    if api:
        headers["Accept"] = "application/vnd.github+json"
        if TOKEN:
            headers["Authorization"] = f"Bearer {TOKEN}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=headers), timeout=30) as response:
        return response.read().decode("utf-8")


class CalendarParser(HTMLParser):
    """Read cell dates and tooltip counts without depending on attribute order."""

    def __init__(self):
        super().__init__()
        self.dates = {}
        self.tips = {}
        self.current = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "data-date" in attrs and "id" in attrs:
            self.dates[attrs["id"]] = dt.date.fromisoformat(attrs["data-date"])
        if tag == "tool-tip":
            self.current = attrs.get("for")
            self.tips[self.current] = ""

    def handle_data(self, data):
        if self.current is not None:
            self.tips[self.current] += data

    def handle_endtag(self, tag):
        if tag == "tool-tip":
            self.current = None


def contributions():
    parser = CalendarParser()
    parser.feed(get(f"https://github.com/users/{USER}/contributions", api=False))
    days = []
    for cell, date in parser.dates.items():
        label = parser.tips.get(cell, "").strip()
        match = re.match(r"([\d,]+) contributions?\b", label)
        if match:
            count = int(match[1].replace(",", ""))
        elif label.lower().startswith("no contributions"):
            count = 0
        else:
            raise ValueError(f"Unknown contribution tooltip for {date}; preserving previous charts")
        days.append((date, count))
    days.sort()
    if len(days) < 300 or any((b[0] - a[0]).days != 1 for a, b in zip(days, days[1:])):
        raise ValueError("Incomplete contribution calendar; preserving previous charts")
    return days


def repos_and_languages():
    repos = []
    page = 1
    while True:
        batch = json.loads(get(f"https://api.github.com/users/{USER}/repos?per_page=100&type=owner&page={page}"))
        repos.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    own = [repo for repo in repos if not repo["fork"] and repo["name"].lower() != USER.lower()]
    share = defaultdict(float)
    for repo in own:
        languages = json.loads(get(repo["languages_url"]))
        total = sum(languages.values())
        if total:
            for name, size in languages.items():
                share[name] += size / total
    return len(own), sorted(share.items(), key=lambda item: (-item[1], item[0]))


def text(x, y, value, size=14, cls="text", **attrs):
    attributes = " ".join(f'{key.replace("_", "-")}="{value}"' for key, value in attrs.items())
    return f'<text x="{x}" y="{y}" font-size="{size}" class="{cls}" {attributes}>{escape(str(value))}</text>'


def svg(width, height, title, description, body):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title><desc id="desc">{escape(description)}</desc>
<style>
text{{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif}}
.bg{{fill:#ffffff;stroke:#d0d7de}}.text{{fill:#1f2328}}.muted{{fill:#59636e}}
.track{{fill:#eaeef2}}.grid{{stroke:#eaeef2}}.accent{{fill:#0969da}}.icon{{stroke:#0969da;fill:none;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}}
@media(prefers-color-scheme:dark){{.bg{{fill:#0d1117;stroke:#30363d}}.text{{fill:#e6edf3}}.muted{{fill:#9da7b3}}.track{{fill:#21262d}}.grid{{stroke:#21262d}}.accent{{fill:#58a6ff}}.icon{{stroke:#58a6ff}}}}
</style>
<rect class="bg" x="0.5" y="0.5" width="{width-1}" height="{height-1}" rx="10"/>
{body}
</svg>\n'''


def stats_card(days, n_repos, today):
    total = sum(count for _, count in days)
    active = sum(count > 0 for _, count in days)
    weeks = defaultdict(int)
    for day, count in days:
        weeks[day - dt.timedelta(days=day.weekday())] += count
    values = list(weeks.values())
    ceiling = max(5, math.ceil(max(values, default=0) / 5) * 5)
    body = text(24, 34, "Contribution activity", 19, font_weight="600")
    body += text(24, 58, f"{days[0][0]:%b %Y} – {days[-1][0]:%b %Y} · weekly totals", 12, "muted")
    body += text(24, 99, f"{total:,}", 29, font_weight="600")
    body += text(24, 120, "contributions", 12, "muted")
    body += text(187, 98, active, 25, font_weight="600")
    body += text(187, 120, "active days", 12, "muted")
    body += text(326, 98, n_repos, 25, font_weight="600")
    body += text(326, 120, "public repos", 12, "muted")
    x0, y0, width, height = 48, 222, 366, 72
    for value in (0, ceiling / 2, ceiling):
        y = y0 - value / ceiling * height
        body += f'<path class="grid" d="M{x0} {y}h{width}"/>'
        body += text(39, y + 4, f"{value:g}", 10, "muted", text_anchor="end")
    step = width / len(values)
    for index, (start, count) in enumerate(weeks.items()):
        bar_height = count / ceiling * height
        body += f'<rect class="accent" x="{x0+index*step:.2f}" y="{y0-bar_height:.2f}" width="{max(1, step-2):.2f}" height="{bar_height:.2f}" rx="1"><title>Week of {start}: {count} contributions</title></rect>'
    body += text(x0, 240, f"{days[0][0]:%b %Y}", 10, "muted")
    body += text(414, 240, f"{days[-1][0]:%b %Y}", 10, "muted", text_anchor="end")
    body += text(24, 268, f"GitHub contribution calendar · updated {today:%d %b %Y}", 10, "muted")
    return svg(440, 286, "GitHub contribution activity", f"{total} contributions over {active} active days. Weekly bars use a zero baseline. Counts follow the public GitHub contribution calendar.", body)


def languages_card(share, today):
    top = share[:5]
    if len(share) > 5:
        top.append(("Other", sum(value for _, value in share[5:])))
    total = sum(value for _, value in top)
    colors = ["#3572a5", "#3178c6", "#b59410", "#168ca6", "#8250df", "#6e7781"]
    body = text(24, 34, "Languages across projects", 19, font_weight="600")
    body += text(24, 58, "Public repositories · excluding forks and this profile", 12, "muted")
    summary = []
    for index, (name, value) in enumerate(top):
        fraction = value / total if total else 0
        y = 89 + index * 27
        body += text(24, y, name, 12)
        body += f'<rect class="track" x="164" y="{y-9}" width="194" height="7" rx="3.5"/>'
        body += f'<rect x="164" y="{y-9}" width="{194*fraction:.2f}" height="7" rx="3.5" fill="{colors[index]}"/>'
        body += text(416, y, f"{fraction:.1%}", 12, "muted", text_anchor="end")
        summary.append(f"{name}: {fraction:.1%}")
    if not top:
        body += text(24, 115, "No language data available.", 14, "muted")
    body += text(24, 250, "Each repository has equal weight, split by code bytes.", 10, "muted")
    body += text(24, 268, f"GitHub language data · updated {today:%d %b %Y}", 10, "muted")
    return svg(440, 286, "Languages across public projects", "; ".join(summary) + ". Repository-weighted code distribution, not skill proficiency.", body)


def stack_card():
    groups = [
        (24, 26, "Languages", "Python · C++ · C · TypeScript", "JavaScript · MATLAB · Verilog", '<path d="m8 6-6 6 6 6m8-12 6 6-6 6m-3-16-3 20"/>'),
        (464, 26, "Machine learning & vision", "PyTorch · CUDA · OpenCV", "NumPy · SciPy · OpenUSD", '<circle cx="4" cy="5" r="3"/><circle cx="20" cy="5" r="3"/><circle cx="12" cy="21" r="3"/><path d="M7 5h10M5.5 8l5 10m8-10-5 10"/>'),
        (24, 151, "Software & infrastructure", "React · Next.js · FastAPI", "Docker · Google Cloud · GitHub Actions", '<rect x="1" y="2" width="22" height="9" rx="2"/><rect x="1" y="15" width="22" height="9" rx="2"/><path d="M5 6.5h1m-1 13h1m5-13h8m-8 13h8"/>'),
        (464, 151, "Hardware & design", "FPGA development · Quartus", "LTspice · SolidWorks", '<rect x="5" y="5" width="16" height="16" rx="2"/><rect x="9" y="9" width="8" height="8" rx="1"/><path d="M9 1v4m8-4v4M9 21v4m8-4v4M1 9h4m-4 8h4M21 9h4m-4 8h4"/>'),
    ]
    body = '<path class="grid" d="M450 24v230M24 136h852"/>'
    for x, y, title, first, second, icon in groups:
        body += f'<g class="icon" transform="translate({x},{y})">{icon}</g>'
        body += text(x+40, y+19, title, 19, font_weight="600")
        body += text(x, y+58, first, 16)
        body += text(x, y+86, second, 16, "muted")
    return svg(900, 278, "Technical stack", "Languages, machine learning and vision, software and infrastructure, and hardware and design tools.", body)


def main():
    today = dt.datetime.now(dt.timezone.utc).date()
    days = contributions()
    n_repos, share = repos_and_languages()
    cards = {
        ASSETS / "stack.svg": stack_card(),
        ASSETS / "generated" / "stats.svg": stats_card(days, n_repos, today),
        ASSETS / "generated" / "languages.svg": languages_card(share, today),
    }
    # Fetch and validate all data before replacing any current assets.
    for path, content in cards.items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8", newline="\n")
        print(f"Wrote {path.name}")


if __name__ == "__main__":
    main()
