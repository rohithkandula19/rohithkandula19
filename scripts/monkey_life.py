#!/usr/bin/env python3
"""Rohi — the resident profile monkey, photographed in the wild.

Four cinematic AI-generated photos of the same capuchin (Higgsfield /
Nano Banana Pro, character-consistent via reference image) live in
assets/rohi/. This script picks the one matching Rohi's real schedule
on Charlotte time and rewrites the README block between the
<!-- ROHI:START --> / <!-- ROHI:END --> markers, with a live caption
(time + today's contribution count = bananas he's been fed).

Stdlib only. Run by the "Rohi's day" workflow every 2 hours.
Set ROHI_ACT=<sleeping|eating|playing|fighting> to force a scene.
"""
import datetime
import json
import os
import re
import urllib.request
import zoneinfo

USER = "rohithkandula19"
README = os.path.join(os.path.dirname(__file__), "..", "README.md")

SCENES = {
    "sleeping": "fast asleep on his branch — belly full, uncle mode 💤",
    "eating": "having bananas on the log 🍌",
    "playing": "swinging through the canopy",
    "fighting": "play-wrestling his cousin 🥊",
}


def pick_activity(hour):
    if hour >= 22 or hour < 6:
        return "sleeping"
    if hour < 9:
        return "eating"
    if hour < 12:
        return "playing"
    if hour < 14:
        return "eating"
    if hour < 17:
        return "fighting"
    if hour < 19:
        return "playing"
    return "eating"


def bananas_today():
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        return None
    query = """
    query($login: String!) {
      user(login: $login) {
        contributionsCollection {
          contributionCalendar { weeks { contributionDays { contributionCount date } } }
        }
      }
    }"""
    try:
        req = urllib.request.Request(
            "https://api.github.com/graphql",
            data=json.dumps({"query": query, "variables": {"login": USER}}).encode(),
            headers={"Authorization": f"Bearer {token}", "User-Agent": "rohi/3.0"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.load(resp)
        days = [
            d
            for w in data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
            for d in w["contributionDays"]
        ]
        today = datetime.datetime.now(zoneinfo.ZoneInfo("America/New_York")).date().isoformat()
        return next((d["contributionCount"] for d in days if d["date"] == today), 0)
    except Exception:
        return None


def main():
    now = datetime.datetime.now(zoneinfo.ZoneInfo("America/New_York"))
    act = os.environ.get("ROHI_ACT") or pick_activity(now.hour)
    fed = bananas_today()

    caption = f"Rohi is {SCENES[act]} · {now.strftime('%-I:%M %p')} in Charlotte"
    if fed is not None:
        caption += f" · fed {fed} 🍌 today" if fed else " · hungry — a git push feeds him 🍌"

    block = f"""
<div align="center">

<img src="assets/rohi/{act}.svg" width="100%" alt="Rohi the capuchin monkey, currently {act}"/>

<sub>📷 <b>{caption}</b> · the photo rotates with his real schedule, every 2 hours</sub>

</div>
"""
    with open(README, encoding="utf-8") as f:
        text = f.read()
    new = re.sub(
        r"(<!-- ROHI:START -->)(.*?)(<!-- ROHI:END -->)",
        lambda m: m.group(1) + block + m.group(3),
        text,
        flags=re.DOTALL,
    )
    if new == text and "<!-- ROHI:START -->" not in text:
        raise SystemExit("ROHI markers missing from README")
    with open(README, "w", encoding="utf-8") as f:
        f.write(new)
    print(f"README updated — {act} at {now:%H:%M %Z}, fed={fed}")


if __name__ == "__main__":
    main()
