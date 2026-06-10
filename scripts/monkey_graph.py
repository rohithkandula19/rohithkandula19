#!/usr/bin/env python3
"""The Contribution Jungle — render the GitHub contribution calendar as a
jungle: banana bunches where commits happened, and a monkey swinging across.

Custom animated SVG (SMIL), no third-party services. Stdlib only.
Requires GITHUB_TOKEN. Output: dist/monkey-jungle.svg
"""
import json
import os
import urllib.request

USER = "rohithkandula19"
OUT = os.path.join(os.path.dirname(__file__), "..", "dist", "monkey-jungle.svg")

CELL = 11          # cell box size
GAP = 2
PAD_X = 12
GRAPH_TOP = 58     # leave headroom for the vine + monkey
THEMES = {
    "": {  # dark (default file keeps its original name)
        "levels": ["#16241a", "#0e4429", "#006d32", "#26a641", "#39d353"],
        "vine": "#3c5a3c",
        "caption": "#7d8590",
    },
    "-light": {
        "levels": ["#e8f0e8", "#9be9a8", "#40c463", "#30a14e", "#216e39"],
        "vine": "#4a7a4a",
        "caption": "#57606a",
    },
}


def fetch_weeks():
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar { weeks { contributionDays { contributionCount date } } }
        }
      }
    }"""
    req = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": query, "variables": {"login": USER}}).encode(),
        headers={
            "Authorization": f"Bearer {os.environ['GITHUB_TOKEN']}",
            "User-Agent": "monkey-jungle/1.0",
        },
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    return data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]


def level(count, maximum):
    if count <= 0:
        return 0
    if maximum <= 4:
        return min(count, 4)
    import math
    return max(1, min(4, math.ceil(4 * count / maximum)))


def build_svg(weeks, theme):
    n_weeks = len(weeks)
    width = PAD_X * 2 + n_weeks * (CELL + GAP)
    height = GRAPH_TOP + 7 * (CELL + GAP) + 30
    maximum = max(
        (d["contributionCount"] for w in weeks for d in w["contributionDays"]),
        default=1,
    )

    cells, bananas = [], []
    counts = sorted(
        d["contributionCount"] for w in weeks for d in w["contributionDays"]
        if d["contributionCount"] > 0
    )
    # bananas only on the busiest ~25% of active days, so it reads as treats not noise
    banana_cut = counts[int(len(counts) * 0.75)] if counts else 1

    for wi, week in enumerate(weeks):
        for di, day in enumerate(week["contributionDays"]):
            x = PAD_X + wi * (CELL + GAP)
            y = GRAPH_TOP + di * (CELL + GAP)
            lv = level(day["contributionCount"], maximum)
            cells.append(
                f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="2.5" '
                f'fill="{theme["levels"][lv]}"><title>{day["date"]}: '
                f'{day["contributionCount"]} contributions</title></rect>'
            )
            if day["contributionCount"] >= banana_cut and day["contributionCount"] > 0:
                bananas.append(
                    f'<text x="{x + CELL / 2}" y="{y + CELL - 1.5}" font-size="9" '
                    f'text-anchor="middle">🍌</text>'
                )

    # vine: gentle scallops across the top
    vine_y = 26
    vine = f"M 0,{vine_y}"
    x = 0
    while x < width:
        vine += f" q {30},{14} {60},0"
        x += 60

    # monkey swing path: out and back, dipping between vine anchors
    fwd, x = f"M {PAD_X},{vine_y + 6}", PAD_X
    while x < width - 70:
        fwd += f" q 30,26 60,0"
        x += 60
    back = ""
    while x > PAD_X:
        back += f" q -30,26 -60,0"
        x -= 60

    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" aria-label="contribution jungle">
  <path d="{vine}" fill="none" stroke="{theme["vine"]}" stroke-width="3" stroke-linecap="round"/>
  <g font-size="10">{''.join(f'<text x="{vx}" y="{vine_y + 16}">🌿</text>' for vx in range(45, width, 120))}</g>
  {''.join(cells)}
  {''.join(bananas)}
  <g>
    <text x="0" y="6" font-size="22" text-anchor="middle">🐒</text>
    <animateMotion dur="26s" repeatCount="indefinite" path="{fwd} {back}"/>
  </g>
  <text x="{PAD_X}" y="{height - 10}" font-size="11" fill="{theme["caption"]}" font-family="ui-monospace, monospace">the contribution jungle — 🍌 grow where the commits are, 🐒 regenerated every 6h</text>
</svg>"""


def main():
    weeks = fetch_weeks()
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    for suffix, theme in THEMES.items():
        path = OUT.replace(".svg", f"{suffix}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(build_svg(weeks, theme))
        print(f"{os.path.basename(path)} written ({len(weeks)} weeks)")


if __name__ == "__main__":
    main()
