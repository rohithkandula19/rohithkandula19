#!/usr/bin/env python3
"""Rohi game engine — the brain behind the playable profile monkey.

Rohi lives on Charlotte time. Every 2 hours the "Rohi's day" workflow
runs `tick`: his activity follows his daily schedule, today's GitHub
contributions become bananas (food = hunger), energy is spent by day and
recovered while sleeping, and happiness drifts back to baseline plus a
boost from anyone who played with him recently.

Visitors play by opening prefilled issues (rohi:feed, rohi:dance, ...);
the "Rohi plays" workflow runs `action`, which applies the effect,
awards XP, records the playmate, and prints a one-line reply for the
issue as the LAST line on stdout.

Both subcommands save data/rohi_state.json, re-render assets/rohi/rohi.svg
via scripts/rohi_game/render_rohi.py, and rewrite the README block between
<!-- ROHI:START --> and <!-- ROHI:END -->.

Stdlib only. Python 3.11+.
"""
import argparse
import datetime
import json
import math
import os
import random
import re
import subprocess
import sys
import urllib.parse
import urllib.request
import zoneinfo

USER = "rohithkandula19"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
STATE_PATH = os.path.join(ROOT, "data", "rohi_state.json")
README_PATH = os.path.join(ROOT, "README.md")
SVG_PATH = os.path.join(ROOT, "assets", "rohi", "rohi.svg")
RENDERER = os.path.join(ROOT, "scripts", "rohi_game", "render_rohi.py")
ET = zoneinfo.ZoneInfo("America/New_York")

SCHEMA = 1
ACTIVITIES = ("eating", "sleeping", "dancing", "running", "playing", "fighting", "idle")

# Rohi's day on Charlotte time (same voice as the original monkey_life.py).
SCENES = {
    "sleeping": "fast asleep, belly full, uncle mode 💤",
    "eating": "having bananas on the log 🍌",
    "playing": "swinging through the canopy",
    "fighting": "play-wrestling his cousin 🥊",
    "dancing": "busting tail-spin moves under the fireflies 🕺",
    "running": "doing canopy sprints, cheeks flapping 🏃",
    "idle": "chilling on his branch, watching the stars",
}

# Player actions: xp on win / xp on loss (None = no contest).
XP = {
    "feed": (10, None),
    "pet": (5, None),
    "dance": (15, None),
    "wrestle": (25, 10),
    "race": (20, 8),
}
PLAYER_ACTIONS = tuple(XP)

# Button row: action -> (emoji, label, badge color, prefilled issue body).
BUTTONS = {
    "feed": ("🍌", "Feed", "ffd54f",
             'Click "Submit new issue" and Rohi gets a banana. The scene updates in ~30s.'),
    "dance": ("🕺", "Dance", "e040fb",
              'Click "Submit new issue" and Rohi busts a move for you. The scene updates in ~30s.'),
    "wrestle": ("🤼", "Wrestle", "ef5350",
                'Click "Submit new issue" to challenge Rohi in the canopy ring. The scene updates in ~30s.'),
    "race": ("🏃", "Race", "42a5f5",
             'Click "Submit new issue" to race Rohi through the treetops. The scene updates in ~30s.'),
    "pet": ("❤️", "Pet", "ec407a",
            'Click "Submit new issue" to give Rohi head pats. The scene updates in ~30s.'),
}

START_MARK = "<!-- ROHI:START -->"
END_MARK = "<!-- ROHI:END -->"


# ---------------------------------------------------------------- time

def now_et():
    """Charlotte wall clock. ROHI_NOW=2026-06-10T21:00:00 pins it for tests."""
    forced = os.environ.get("ROHI_NOW")
    if forced:
        dt = datetime.datetime.fromisoformat(forced)
        return dt if dt.tzinfo else dt.replace(tzinfo=ET)
    return datetime.datetime.now(ET)


def now_utc():
    return now_et().astimezone(datetime.timezone.utc)


def iso_utc():
    return now_utc().replace(microsecond=0).isoformat()


# ------------------------------------------------------------ schedule

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
        return "running"
    if hour < 21:
        return "dancing"
    return "idle"


# --------------------------------------------------------------- state

def default_state():
    return {
        "schema": SCHEMA,
        "activity": "idle",
        "hunger": 70,
        "energy": 70,
        "happiness": 60,
        "xp": 0,
        "level": 1,
        "bananas_today": 0,
        "bananas_total": 0,
        "wins": 0,
        "losses": 0,
        "races_won": 0,
        "dances": 0,
        "pets": 0,
        "recent_players": [],
        "last_tick_utc": iso_utc(),
        "updated_utc": iso_utc(),
    }


def load_state():
    try:
        with open(STATE_PATH, encoding="utf-8") as f:
            raw = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default_state()
    state = default_state()
    state.update({k: raw[k] for k in state if k in raw})
    return state


def save_state(state):
    state["updated_utc"] = iso_utc()
    os.makedirs(os.path.dirname(STATE_PATH), exist_ok=True)
    with open(STATE_PATH, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
        f.write("\n")


def clamp(value, lo=0, hi=100):
    return max(lo, min(hi, int(value)))


def level_for(xp):
    return 1 + math.floor(math.sqrt(max(0, xp) / 50))


# ------------------------------------------------------------- bananas

def bananas_today():
    """Today's contribution count via GraphQL — Rohi's food. None on failure."""
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
            headers={"Authorization": f"Bearer {token}", "User-Agent": "rohi/4.0"},
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = json.load(resp)
        days = [
            d
            for w in data["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
            for d in w["contributionDays"]
        ]
        today = now_et().date().isoformat()
        return next((d["contributionCount"] for d in days if d["date"] == today), 0)
    except Exception:
        return None


# ------------------------------------------------- render + README block

def render_svg(state):
    subprocess.run(
        [sys.executable, RENDERER, "--state", STATE_PATH, "--out", SVG_PATH],
        cwd=ROOT,
        check=True,
        capture_output=True,  # keep engine stdout clean: the reply must be last
        text=True,
    )


def badge_md(action):
    emoji, label, color, body = BUTTONS[action]
    issue_url = "https://github.com/{0}/{0}/issues/new?{1}".format(
        USER,
        urllib.parse.urlencode(
            {"title": f"rohi:{action}", "body": body},
            quote_via=urllib.parse.quote_plus,
        ),
    )
    content = urllib.parse.quote(f"{emoji} {label}").replace("-", "--")
    badge_url = f"https://img.shields.io/badge/{content}-{color}?style=flat-square"
    return f"[![{emoji} {label}]({badge_url})]({issue_url})"


def build_block(state, when_et):
    fed = state["bananas_today"]
    fed_bit = f"fed {fed} 🍌 today" if fed else "hungry, somebody push some code 🍌"
    caption = (
        f"Rohi is {SCENES[state['activity']]} · {when_et.strftime('%-I:%M %p')} in Charlotte"
        f" · {fed_bit} · LVL {state['level']} · {state['xp']} XP"
    )
    badges = " ".join(badge_md(a) for a in ("feed", "dance", "wrestle", "race", "pet"))
    players = state["recent_players"]
    if players:
        recent = "Recent playmates: " + " · ".join(
            f"@{p['user']} ({p['action']})" for p in players
        )
    else:
        recent = "No playmates yet — press a button above and be Rohi's first friend 🐒"
    cache_bust = int(now_utc().timestamp())
    return f"""
<div align="center">

<img src="assets/rohi/rohi.svg?v={cache_bust}" width="100%" alt="Rohi the capuchin monkey, currently {state['activity']}"/>

<sub>🎮 <b>{caption}</b></sub>

{badges}

<sub>{recent}</sub>

</div>
"""


def rewrite_readme(state, when_et):
    with open(README_PATH, encoding="utf-8") as f:
        text = f.read()
    if START_MARK not in text or END_MARK not in text:
        raise SystemExit("ROHI markers missing from README")
    block = build_block(state, when_et)
    new = re.sub(
        rf"({re.escape(START_MARK)})(.*?)({re.escape(END_MARK)})",
        lambda m: m.group(1) + block + m.group(3),
        text,
        flags=re.DOTALL,
    )
    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new)


def persist_everything(state, when_et):
    """Contract order: save state first (the renderer reads it), then render, then README."""
    save_state(state)
    render_svg(state)
    rewrite_readme(state, when_et)


# ----------------------------------------------------------------- tick

def recent_boost(state, when_utc):
    """Happiness boost from players who showed up within the last 24h."""
    boost = 0
    for p in state["recent_players"]:
        try:
            at = datetime.datetime.fromisoformat(p["at"])
        except (KeyError, ValueError):
            continue
        if at.tzinfo is None:
            at = at.replace(tzinfo=datetime.timezone.utc)
        if (when_utc - at) <= datetime.timedelta(hours=24):
            boost += 2
    return min(boost, 12)


def cmd_tick():
    state = load_state()
    when = now_et()
    state["activity"] = os.environ.get("ROHI_ACT") or pick_activity(when.hour)
    if state["activity"] not in ACTIVITIES:
        state["activity"] = "idle"

    fed = bananas_today()
    if fed is not None:
        prev = state["bananas_today"]
        new_bananas = fed if fed < prev else fed - prev  # smaller = new day rolled over
        state["bananas_total"] += new_bananas
        state["xp"] += 2 * new_bananas
        state["bananas_today"] = fed
        state["hunger"] = clamp(40 + 6 * fed)

    if state["activity"] == "sleeping":
        state["energy"] = clamp(state["energy"] + 15)
    elif state["activity"] in ("eating", "idle"):
        state["energy"] = clamp(state["energy"] + 3)
    elif state["activity"] in ("running", "fighting"):
        state["energy"] = clamp(state["energy"] - 10)
    else:  # playing, dancing
        state["energy"] = clamp(state["energy"] - 7)

    h = state["happiness"]
    drift = max(-4, min(4, 60 - h))
    state["happiness"] = clamp(h + drift + recent_boost(state, when.astimezone(datetime.timezone.utc)))

    state["level"] = level_for(state["xp"])
    state["last_tick_utc"] = iso_utc()
    persist_everything(state, when)
    print(
        f"tick — {state['activity']} at {when:%H:%M %Z}, fed={fed}, "
        f"hunger={state['hunger']} energy={state['energy']} happiness={state['happiness']} "
        f"lvl={state['level']} xp={state['xp']}"
    )


# --------------------------------------------------------------- action

def sanitize_user(user):
    user = re.sub(r"[^A-Za-z0-9-]", "", user or "")[:39]
    return user or "friend"


def contest(user, kind, win_chance):
    """Deterministic-per-hour coin flip, seeded by (user, utcnow hour)."""
    rng = random.Random(f"{user}:{kind}:{now_utc():%Y-%m-%dT%H}")
    return rng.random() < win_chance


def cmd_action(action, user):
    user = sanitize_user(user)
    if action not in PLAYER_ACTIONS:
        # Stay graceful so the workflow can still comment + close the issue.
        print(f"@{user} tried '{action}', but Rohi only knows feed, dance, wrestle, race and pet. He tilts his head at you. 🐒")
        return

    state = load_state()
    when = now_et()
    win_xp, lose_xp = XP[action]

    if action == "feed":
        state["hunger"] = clamp(state["hunger"] + 12)
        state["bananas_total"] += 1
        state["xp"] += win_xp
        reply = (
            f"@{user} fed Rohi a banana! hunger {state['hunger']}/100, "
            f"that's banana #{state['bananas_total']} in his lifetime stash. He salutes you with his tail. 🍌"
        )
    elif action == "pet":
        state["happiness"] = clamp(state["happiness"] + 8)
        state["pets"] += 1
        state["xp"] += win_xp
        reply = (
            f"@{user} gave Rohi head pats! happiness {state['happiness']}/100. "
            f"He leans in for one more. ❤️"
        )
    elif action == "dance":
        state["activity"] = "dancing"
        state["happiness"] = clamp(state["happiness"] + 10)
        state["dances"] += 1
        state["xp"] += win_xp
        reply = (
            f"@{user} started a dance party! happiness {state['happiness']}/100 "
            f"after dance #{state['dances']}. Rohi hits the tail-spin. 🕺"
        )
    elif action == "wrestle":
        state["activity"] = "fighting"
        if contest(user, "wrestle", 0.55):
            state["wins"] += 1
            state["xp"] += win_xp
            reply = (
                f"Rohi pinned @{user} in the canopy ring! record {state['wins']}W-{state['losses']}L. "
                f"He flexes a tiny bicep at you. 🤼"
            )
        else:
            state["losses"] += 1
            state["xp"] += lose_xp
            reply = (
                f"@{user} out-wrestled Rohi! record {state['wins']}W-{state['losses']}L. "
                f"He demands a rematch right after snacks. 🤼"
            )
    else:  # race
        state["activity"] = "running"
        if contest(user, "race", 0.50):
            state["races_won"] += 1
            state["xp"] += win_xp
            reply = (
                f"Rohi smoked @{user} through the treetops! that's race win #{state['races_won']}. "
                f"He does a victory lap on two fingers. 🏃"
            )
        else:
            state["xp"] += lose_xp
            reply = (
                f"@{user} outran Rohi to the big banana tree! race wins stay at {state['races_won']}. "
                f"He blames a slippery branch. 🏃"
            )

    old_level = state["level"]
    state["level"] = level_for(state["xp"])
    if state["level"] > old_level:
        reply += f" LEVEL UP — Rohi is now LVL {state['level']}!"

    state["recent_players"].insert(0, {"user": user, "action": action, "at": iso_utc()})
    state["recent_players"] = state["recent_players"][:6]

    persist_everything(state, when)
    print(reply)  # MUST be the last stdout line — the workflow posts it on the issue


# ----------------------------------------------------------------- main

def main():
    parser = argparse.ArgumentParser(description="Rohi game engine")
    sub = parser.add_subparsers(dest="cmd", required=True)
    sub.add_parser("tick", help="scheduled life tick")
    act = sub.add_parser("action", help="player action from an issue")
    act.add_argument("--type", required=True, dest="type_")
    act.add_argument("--user", required=True)
    args = parser.parse_args()
    if args.cmd == "tick":
        cmd_tick()
    else:
        cmd_action(args.type_.strip().lower(), args.user)


if __name__ == "__main__":
    main()
