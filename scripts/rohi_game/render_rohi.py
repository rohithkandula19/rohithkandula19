#!/usr/bin/env python3
"""Rohi sprite renderer — draws the whole game scene as ONE animated SVG.

Stdlib only. Safe for GitHub README <img> embedding:
  * no JavaScript, no external resources, system font stack only
  * all animation is CSS @keyframes inside a <style> element, looping forever

Usage:
    python3 scripts/rohi_game/render_rohi.py --state data/rohi_state.json \
        --out assets/rohi/rohi.svg [--activity dancing]

Env:
    ROHI_NOW="2026-06-10T21:00:00"  overrides the wall clock (deterministic
    tests). Naive timestamps are taken as America/New_York local time.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from datetime import datetime
from xml.sax.saxutils import escape
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/New_York")
W, H = 900, 320

ACTIVITIES = ("eating", "sleeping", "dancing", "running", "playing", "fighting", "idle")

# ----------------------------------------------------------------------------
# palette / colours
# ----------------------------------------------------------------------------

BODY = "#4a2f1e"      # capuchin dark brown body
BODY_D = "#36210f"    # darker (feet, hands, shading)
CREAM = "#f4e3c2"     # cream chest
FACE = "#f7ead0"      # cream face
MUZZLE = "#e9d3ac"
INK = "#2a1a10"       # pupils / line work
COUSIN = "#3b2516"    # cousin is a darker, bigger fellow
COUSIN_CREAM = "#e6d2ae"
BANANA = "#ffd54a"
BANANA_EDGE = "#c79a2a"

PALETTES = {
    "day": {
        "sky": ("#5fb2ef", "#a8dcf7", "#e7f6e0"),
        "celestial": "sun",
        "canopy1": "#2e7d4f", "canopy2": "#3e9d5f", "canopy3": "#57b86b",
        "ground": "#4d8f4a", "ground2": "#3f7a3e",
        "log": "#6c4a2f", "log2": "#7d5a3a", "moss": "#5aa45a",
        "stars": False, "fireflies": False,
    },
    "dusk": {
        "sky": ("#5b3a78", "#d8623f", "#ffb347"),
        "celestial": "dusksun",
        "canopy1": "#1f5e3e", "canopy2": "#2c724a", "canopy3": "#3f8f58",
        "ground": "#3f6e3c", "ground2": "#345c32",
        "log": "#5d3f29", "log2": "#6d4e33", "moss": "#4c8c4c",
        "stars": False, "fireflies": False,
    },
    "night": {
        "sky": ("#070d2c", "#14204e", "#23355f"),
        "celestial": "moon",
        "canopy1": "#0f3826", "canopy2": "#174530", "canopy3": "#1f5a3c",
        "ground": "#1d3d22", "ground2": "#16301b",
        "log": "#4a3322", "log2": "#57402c", "moss": "#2f6b3f",
        "stars": True, "fireflies": True,
    },
}

CAPTIONS = {
    "eating": "Rohi is munching a banana",
    "sleeping": "Rohi is fast asleep",
    "dancing": "Rohi is busting moves",
    "running": "Rohi is on a jungle sprint",
    "playing": "Rohi is swinging through the canopy",
    "fighting": "Rohi is wrestling his big cousin",
    "idle": "Rohi is chilling and grooming",
}

FONT = "'Segoe UI',Helvetica,Arial,sans-serif"
FAM = FONT.replace("'", "&apos;")  # XML-safe form for font-family attributes

# ----------------------------------------------------------------------------
# tiny helpers
# ----------------------------------------------------------------------------


def n(v) -> str:
    """Compact number formatting for SVG/CSS."""
    s = f"{float(v):.2f}".rstrip("0").rstrip(".")
    return s if s not in ("", "-0") else "0"


def kf(name: str, stops) -> str:
    """stops: list of (percent, css-declarations) -> @keyframes block."""
    inner = "".join(f"{n(p)}%{{{d}}}" for p, d in stops)
    return "@keyframes " + name + "{" + inner + "}"


def rot(cx, cy, deg, pre="") -> str:
    """Transform decl: rotate `deg` about local point (cx, cy)."""
    return (f"transform:{pre}translate({n(cx)}px,{n(cy)}px) rotate({n(deg)}deg) "
            f"translate({n(-cx)}px,{n(-cy)}px);")


def scale_at(cx, cy, sx, sy, pre="") -> str:
    return (f"transform:{pre}translate({n(cx)}px,{n(cy)}px) scale({n(sx)},{n(sy)}) "
            f"translate({n(-cx)}px,{n(-cy)}px);")


def circle(cx, cy, r, fill, extra="") -> str:
    return f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="{fill}" {extra}/>'


def ellipse(cx, cy, rx, ry, fill, extra="") -> str:
    return (f'<ellipse cx="{n(cx)}" cy="{n(cy)}" rx="{n(rx)}" ry="{n(ry)}" '
            f'fill="{fill}" {extra}/>')


def limb(d, w=8, color=BODY, extra="") -> str:
    return (f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{n(w)}" '
            f'stroke-linecap="round" {extra}/>')


def star_path(cx, cy, points, r1, r2, rot_deg=0.0) -> str:
    pts = []
    for i in range(points * 2):
        r = r1 if i % 2 == 0 else r2
        a = math.radians(rot_deg) + math.pi * i / points
        pts.append(f"{n(cx + r * math.sin(a))},{n(cy - r * math.cos(a))}")
    return "M" + " L".join(pts) + " Z"


def _lcg(seed: int):
    x = seed & 0x7FFFFFFF
    while True:
        x = (x * 1103515245 + 12345) & 0x7FFFFFFF
        yield x / 0x7FFFFFFF


# ----------------------------------------------------------------------------
# state / time
# ----------------------------------------------------------------------------

DEFAULT_STATE = {
    "schema": 1, "activity": "idle",
    "hunger": 70, "energy": 70, "happiness": 70,
    "xp": 0, "level": 1,
    "bananas_today": 0, "bananas_total": 0,
    "wins": 0, "losses": 0, "races_won": 0, "dances": 0, "pets": 0,
    "recent_players": [],
    "last_tick_utc": "", "updated_utc": "",
}


def load_state(path: str) -> dict:
    state = dict(DEFAULT_STATE)
    try:
        with open(path, "r", encoding="utf-8") as fh:
            raw = json.load(fh)
        if isinstance(raw, dict):
            state.update(raw)
    except FileNotFoundError:
        print(f"render_rohi: state file {path!r} missing, using defaults", file=sys.stderr)
    except (json.JSONDecodeError, OSError) as exc:
        print(f"render_rohi: could not read state ({exc}), using defaults", file=sys.stderr)
    return state


def now_charlotte() -> datetime:
    raw = os.environ.get("ROHI_NOW", "").strip()
    if raw:
        try:
            dt = datetime.fromisoformat(raw)
            return dt.astimezone(TZ) if dt.tzinfo else dt.replace(tzinfo=TZ)
        except ValueError:
            print(f"render_rohi: bad ROHI_NOW {raw!r}, using real clock", file=sys.stderr)
    return datetime.now(TZ)


def sky_phase(dt: datetime) -> str:
    h = dt.hour
    if 6 <= h < 19:
        return "day"
    if 19 <= h < 21:
        return "dusk"
    return "night"


# ----------------------------------------------------------------------------
# shared monkey parts (drawn in a local frame; caller wraps in translate())
# ----------------------------------------------------------------------------


def head_svg(cx, cy, s=1.0, eyes="open", mouth="smile", brows=False,
             eye_cls="", mouth_cls="", cheek_cls="", body=BODY, face=FACE,
             muzzle=MUZZLE, look=0.0) -> str:
    """A capuchin head: dark cap, cream face, big eyes. `look` shifts features x."""
    o = []
    # ears
    for sx in (-1, 1):
        o.append(circle(cx + sx * 19 * s, cy - 1 * s, 7.5 * s, body))
        o.append(circle(cx + sx * 19 * s, cy - 1 * s, 3.8 * s, muzzle))
    # skull (dark cap shows above the cream face)
    o.append(circle(cx, cy, 20 * s, body))
    # cream face
    o.append(ellipse(cx + look * s, cy + 4 * s, 15.5 * s, 14 * s, face))
    # cheek puff (eating)
    if cheek_cls:
        o.append(ellipse(cx + (look + 9) * s, cy + 8 * s, 6 * s, 5 * s, MUZZLE,
                         f'class="{cheek_cls}"'))
    # muzzle
    o.append(ellipse(cx + look * s, cy + 9.5 * s, 8.5 * s, 6.5 * s, muzzle))
    o.append(circle(cx + (look - 2) * s, cy + 7.5 * s, 0.9 * s, INK))
    o.append(circle(cx + (look + 2) * s, cy + 7.5 * s, 0.9 * s, INK))
    # eyes
    ex, ey = 6.7 * s, cy + 0.5 * s
    e = [f'<g class="{eye_cls}">' if eye_cls else "<g>"]
    if eyes == "open":
        for sx in (-1, 1):
            x = cx + look * s + sx * ex
            e.append(circle(x, ey, 4.4 * s, "#fff"))
            e.append(circle(x + 0.8 * s, ey + 0.5 * s, 2.5 * s, INK))
            e.append(circle(x + 1.7 * s, ey - 0.5 * s, 0.9 * s, "#fff"))
    elif eyes == "happy":
        for sx in (-1, 1):
            x = cx + look * s + sx * ex
            e.append(limb(f"M{n(x - 3.4 * s)},{n(ey + 1.2 * s)} "
                          f"Q{n(x)},{n(ey - 3.6 * s)} {n(x + 3.4 * s)},{n(ey + 1.2 * s)}",
                          1.8 * s, INK))
    else:  # closed
        for sx in (-1, 1):
            x = cx + look * s + sx * ex
            e.append(limb(f"M{n(x - 3.4 * s)},{n(ey - 0.6 * s)} "
                          f"Q{n(x)},{n(ey + 3)} {n(x + 3.4 * s)},{n(ey - 0.6 * s)}",
                          1.8 * s, INK))
    e.append("</g>")
    o.extend(e)
    if brows:
        for sx in (-1, 1):
            x = cx + look * s + sx * ex
            o.append(limb(f"M{n(x - 3.5 * s)},{n(ey - (7 - sx) * s)} "
                          f"L{n(x + 3.5 * s)},{n(ey - (7 + sx) * s)}", 2 * s, INK))
    # mouth
    mx, my = cx + look * s, cy + 12.5 * s
    mc = f'class="{mouth_cls}"' if mouth_cls else ""
    if mouth == "smile":
        o.append(limb(f"M{n(mx - 3.5 * s)},{n(my)} Q{n(mx)},{n(my + 3 * s)} "
                      f"{n(mx + 3.5 * s)},{n(my)}", 1.6 * s, INK))
    elif mouth == "open":
        o.append(ellipse(mx, my + 1 * s, 3.6 * s, 3 * s, INK, mc))
    elif mouth == "o":
        o.append(circle(mx, my + 1 * s, 1.8 * s, INK, mc))
    elif mouth == "grit":
        o.append(limb(f"M{n(mx - 4 * s)},{n(my + 1 * s)} L{n(mx + 4 * s)},{n(my + 1 * s)}",
                      2 * s, INK))
    return "".join(o)


def tail_svg(x, y, flip=1, cls="", color=BODY, w=7) -> str:
    f = flip
    d = (f"M{n(x)},{n(y)} q{n(-24 * f)},-4 {n(-32 * f)},-28 "
         f"q{n(-6 * f)},-22 {n(12 * f)},-30 q{n(16 * f)},-7 {n(22 * f)},6 "
         f"q{n(4 * f)},12 {n(-8 * f)},14 q{n(-10 * f)},1 {n(-9 * f)},-8")
    c = f'class="{cls}"' if cls else ""
    return f'<g {c}>{limb(d, w, color)}</g>'


def banana_svg(cx, cy, deg=0, s=1.0) -> str:
    d = "M-12,0 Q0,13 12,0 Q13,-2 11,-1 Q5,6 0,6 Q-5,6 -11,-1 Q-13,-2 -12,0 Z"
    return (f'<g transform="translate({n(cx)},{n(cy)}) rotate({n(deg)}) scale({n(s)})">'
            f'<path d="{d}" fill="{BANANA}" stroke="{BANANA_EDGE}" stroke-width="0.8"/>'
            f'{circle(-12, 0, 1.3, "#7a5a1e")}{circle(12, 0, 1.3, "#7a5a1e")}</g>')


def note_svg(x, y, s=1.0, color="#ffe9a8") -> str:
    return (f'<g transform="translate({n(x)},{n(y)}) scale({n(s)})">'
            f'<ellipse cx="0" cy="0" rx="4.4" ry="3.1" fill="{color}" '
            f'transform="rotate(-20)"/>'
            f'<path d="M3.8,-1 V-19 q6,1 8,6" fill="none" stroke="{color}" '
            f'stroke-width="2" stroke-linecap="round"/></g>')


# ----------------------------------------------------------------------------
# sitting body (shared by eating / idle); local origin = seat point
# ----------------------------------------------------------------------------


def sitting_body() -> str:
    o = []
    # haunches + feet
    for sx in (-1, 1):
        o.append(ellipse(sx * 14, -12, 14, 10, BODY))
        o.append(ellipse(sx * 16, -3, 9.5, 4.5, BODY_D))
    o.append(ellipse(0, -34, 24, 30, BODY))      # body
    o.append(ellipse(0, -28, 14, 19, CREAM))     # chest
    return "".join(o)


# ----------------------------------------------------------------------------
# scenes — each appends to css[] and returns the foreground svg string
# ----------------------------------------------------------------------------


def scene_eating(css, pal):
    X, Y = 252, 238
    css.append(kf("armEat", [
        (0, "transform:none;"), (10, "transform:none;"),
        (30, rot(12, -50, -115, "translate(-20px,6px) ")),
        (55, rot(12, -50, -115, "translate(-20px,6px) ")),
        (75, "transform:none;"), (100, "transform:none;")]))
    css.append(".armEat{animation:armEat 3.2s ease-in-out infinite;}")
    css.append(kf("cheekP", [
        (0, scale_at(9, -64, 0.2, 0.2) + "opacity:0;"),
        (28, scale_at(9, -64, 0.2, 0.2) + "opacity:0;"),
        (40, scale_at(9, -64, 1.25, 1.25) + "opacity:1;"),
        (62, scale_at(9, -64, 1.25, 1.25) + "opacity:1;"),
        (78, scale_at(9, -64, 0.2, 0.2) + "opacity:0;"),
        (100, scale_at(9, -64, 0.2, 0.2) + "opacity:0;")]))
    css.append(".cheekP{animation:cheekP 3.2s ease-in-out infinite;}")
    css.append(kf("chewM", [(0, scale_at(0, -59, 1, 1)),
                            (50, scale_at(0, -59, 1, 0.35)),
                            (100, scale_at(0, -59, 1, 1))]))
    css.append(".chewM{animation:chewM 0.45s ease-in-out infinite;}")
    css.append(kf("tailSway", [(0, rot(10, -12, -6)), (50, rot(10, -12, 7)),
                               (100, rot(10, -12, -6))]))
    css.append(".tailSway{animation:tailSway 4.5s ease-in-out infinite;}")

    o = [f'<g transform="translate({X},{Y})">']
    o.append(tail_svg(10, -12, flip=-1, cls="tailSway"))
    o.append(sitting_body())
    o.append(head_svg(0, -72, 1.0, eyes="open", mouth="open",
                      mouth_cls="chewM", cheek_cls="cheekP"))
    # resting left arm
    o.append(limb("M-13,-48 Q-28,-38 -24,-18", 8))
    o.append(circle(-24, -18, 5, BODY_D))
    # animated banana arm
    o.append('<g class="armEat">')
    o.append(limb("M12,-50 Q30,-44 26,-22", 8))
    o.append(circle(26, -22, 5.2, BODY_D))
    o.append(banana_svg(30, -25, -42, 1.0))
    o.append("</g></g>")
    # scattered peels by the log
    for px, py, pr in ((318, 276, 20), (352, 282, -35), (180, 280, 70)):
        o.append(f'<g transform="translate({px},{py}) rotate({pr})">'
                 f'<path d="M0,0 q5,-9 12,-5 q-2,7 -12,5 Z" fill="#e8c84a" '
                 f'stroke="{BANANA_EDGE}" stroke-width="0.6"/>'
                 f'<path d="M0,0 q-6,-8 -13,-3 q3,7 13,3 Z" fill="#f0d35e" '
                 f'stroke="{BANANA_EDGE}" stroke-width="0.6"/></g>')
    return "".join(o)


def scene_idle(css, pal):
    X, Y = 252, 238
    css.append(kf("tailSway", [(0, rot(10, -12, -7)), (50, rot(10, -12, 8)),
                               (100, rot(10, -12, -7))]))
    css.append(".tailSway{animation:tailSway 5s ease-in-out infinite;}")
    css.append(kf("groomA", [(0, rot(13, -48, -4)), (100, rot(13, -48, 10))]))
    css.append(".groomA{animation:groomA 0.9s ease-in-out infinite alternate;}")
    css.append(kf("headTilt", [
        (0, rot(0, -54, 0)), (55, rot(0, -54, 0)), (63, rot(0, -54, 9)),
        (78, rot(0, -54, 9)), (86, rot(0, -54, 0)), (100, rot(0, -54, 0))]))
    css.append(".headTilt{animation:headTilt 7s ease-in-out infinite;}")
    css.append(kf("blink", [
        (0, scale_at(0, -71, 1, 1)), (91, scale_at(0, -71, 1, 1)),
        (94, scale_at(0, -71, 1, 0.08)), (97, scale_at(0, -71, 1, 1)),
        (100, scale_at(0, -71, 1, 1))]))
    css.append(".blink{animation:blink 4.6s linear infinite;}")

    o = [f'<g transform="translate({X},{Y})">']
    o.append(tail_svg(10, -12, flip=-1, cls="tailSway"))
    o.append(sitting_body())
    o.append('<g class="headTilt">')
    o.append(head_svg(0, -72, 1.0, eyes="open", mouth="smile", eye_cls="blink"))
    o.append("</g>")
    # left arm held up (being groomed)
    o.append(limb("M-13,-48 Q-30,-40 -18,-26", 8))
    o.append(circle(-18, -26, 5, BODY_D))
    # grooming right arm
    o.append('<g class="groomA">')
    o.append(limb("M13,-48 Q26,-44 2,-30", 8))
    o.append(circle(2, -30, 5, BODY_D))
    o.append("</g></g>")
    return "".join(o)


def scene_sleeping(css, pal):
    X, Y = 255, 226
    css.append(kf("breathe", [(0, scale_at(0, 14, 1, 1)),
                              (50, scale_at(0, 14, 1.03, 1.09)),
                              (100, scale_at(0, 14, 1, 1))]))
    css.append(".breathe{animation:breathe 3.2s ease-in-out infinite;}")
    css.append(kf("zfloat", [
        (0, "opacity:0;transform:translate(0,0);"),
        (18, "opacity:1;"),
        (80, "opacity:0.9;"),
        (100, "opacity:0;transform:translate(20px,-48px);")]))
    css.append(".zfloat{animation:zfloat 4.8s ease-out infinite;}")
    # snoring mouth: little "o" pulsing at the mouth position of the head below
    css.append(kf("snore", [(0, scale_at(-42, 8.8, 1, 1)),
                            (50, scale_at(-42, 8.8, 1.6, 1.6)),
                            (100, scale_at(-42, 8.8, 1, 1))]))
    css.append(".snore{animation:snore 3.2s ease-in-out infinite;}")

    o = [f'<g transform="translate({X},{Y})">']
    # tail dangling off the log
    o.append(limb("M22,12 q8,26 -10,36 q-14,7 -20,-3", 7))
    # torso belly-up, breathing
    o.append('<g class="breathe">')
    o.append(ellipse(0, 0, 33, 18, BODY))
    o.append(ellipse(0, -4, 20, 11, CREAM))
    o.append("</g>")
    # head resting at the left end
    o.append(head_svg(-42, -4, 0.95, eyes="closed", mouth="o", mouth_cls="snore"))
    # arm flopped across the belly, another above the head
    o.append(limb("M-16,-8 Q0,-20 14,-9", 7.5))
    o.append(circle(14, -9, 4.6, BODY_D))
    o.append(limb("M-32,-12 Q-50,-24 -56,-10", 7.5))
    o.append(circle(-56, -10, 4.6, BODY_D))
    # legs and feet up in the air
    o.append(limb("M26,-4 Q40,-22 35,-31", 8))
    o.append(ellipse(35, -33, 7, 4.5, BODY_D))
    o.append(limb("M31,2 Q52,-12 50,-22", 8))
    o.append(ellipse(50, -24, 7, 4.5, BODY_D))
    o.append("</g>")
    # floating Z z z
    fam = FAM
    for zx, zy, fs, dl in ((205, 178, 13, 0.0), (216, 166, 17, 1.6),
                           (228, 152, 22, 3.2)):
        o.append(f'<text x="{zx}" y="{zy}" font-family="{fam}" font-size="{fs}" '
                 f'font-style="italic" font-weight="700" fill="#cfe3ff" '
                 f'class="zfloat" style="animation-delay:-{dl}s">z</text>')
    return "".join(o)


def scene_dancing(css, pal):
    X, Y = 470, 282
    css.append(kf("hips", [(0, rot(0, -20, -6, "translate(0,0) ")),
                           (25, rot(0, -20, 0, "translate(0,-5px) ")),
                           (50, rot(0, -20, 6, "translate(0,0) ")),
                           (75, rot(0, -20, 0, "translate(0,-5px) ")),
                           (100, rot(0, -20, -6, "translate(0,0) "))]))
    css.append(".hips{animation:hips 1.6s ease-in-out infinite;}")
    css.append(kf("armR", [(0, rot(15, -58, -150)), (50, rot(15, -58, -30)),
                           (100, rot(15, -58, -150))]))
    css.append(".armR{animation:armR 1.6s ease-in-out infinite;}")
    css.append(kf("armL", [(0, rot(-15, -58, 30)), (50, rot(-15, -58, 150)),
                           (100, rot(-15, -58, 30))]))
    css.append(".armL{animation:armL 1.6s ease-in-out infinite;}")
    css.append(kf("noteB", [(0, "transform:translate(0,0);opacity:0;"),
                            (20, "opacity:1;"),
                            (50, "transform:translate(4px,-16px);opacity:1;"),
                            (100, "transform:translate(8px,-34px);opacity:0;")]))
    css.append(".noteB{animation:noteB 1.7s ease-out infinite;}")
    css.append(kf("sprk", [(0, "transform:scale(0.1);opacity:0;"),
                           (45, "transform:scale(1);opacity:1;"),
                           (100, "transform:scale(0.1);opacity:0;")]))
    css.append(".sprk{animation:sprk 1.4s ease-in-out infinite;transform-box:fill-box;"
               "transform-origin:center;}")
    css.append(kf("spot", [(0, "opacity:0.05;"), (50, "opacity:0.16;"),
                           (100, "opacity:0.05;")]))
    css.append(".spot{animation:spot 1.6s ease-in-out infinite;}")

    o = []
    # disco spotlights
    o.append(f'<polygon points="430,0 466,0 560,292 380,292" fill="#ff6fae" '
             f'class="spot"/>')
    o.append(f'<polygon points="470,0 506,0 600,292 420,292" fill="#4fc3f7" '
             f'class="spot" style="animation-delay:-0.8s"/>')
    o.append(f'<g transform="translate({X},{Y})">')
    o.append(ellipse(0, 2, 42, 7, "#000", 'opacity="0.18"'))
    # legs planted wide
    o.append(limb("M-10,-26 Q-16,-12 -16,-2", 9))
    o.append(limb("M10,-26 Q16,-12 16,-2", 9))
    o.append(ellipse(-17, -1, 9, 4.5, BODY_D))
    o.append(ellipse(17, -1, 9, 4.5, BODY_D))
    o.append('<g class="hips">')
    o.append(tail_svg(12, -30, flip=-1))
    o.append(ellipse(0, -44, 21, 27, BODY))
    o.append(ellipse(0, -40, 12, 17, CREAM))
    o.append(head_svg(0, -84, 1.0, eyes="happy", mouth="open"))
    o.append('<g class="armR">' + limb("M15,-58 Q31,-50 29,-32", 8) +
             circle(29, -32, 5, BODY_D) + "</g>")
    o.append('<g class="armL">' + limb("M-15,-58 Q-31,-50 -29,-32", 8) +
             circle(-29, -32, 5, BODY_D) + "</g>")
    o.append("</g></g>")
    # bouncing notes + sparkles
    for i, (nx, ny, s) in enumerate(((392, 176, 1.0), (552, 162, 1.25), (508, 198, 0.85))):
        o.append(f'<g class="noteB" style="animation-delay:-{i * 0.55}s">'
                 + note_svg(nx, ny, s) + "</g>")
    for i, (sx, sy, r) in enumerate(((372, 220, 6), (560, 235, 5), (430, 150, 5),
                                     (520, 130, 6.5))):
        o.append(f'<path d="{star_path(sx, sy, 4, r, r * 0.32)}" fill="#fff2b0" '
                 f'class="sprk" style="animation-delay:-{i * 0.35}s"/>')
    return "".join(o)


def scene_running(css, pal):
    # base group sits mid-scene so Rohi is visible the instant the README loads;
    # he exits right, then wraps in from the left while fully off-screen
    css.append(kf("runx", [(0, "transform:translate(0,0);"),
                           (50, "transform:translate(610px,0);"),
                           (50.01, "transform:translate(-610px,0);"),
                           (100, "transform:translate(0,0);")]))
    css.append(".runx{animation:runx 6.5s linear infinite;}")
    css.append(kf("bob", [(0, "transform:translate(0,0);"),
                          (50, "transform:translate(0,-6px);"),
                          (100, "transform:translate(0,0);")]))
    css.append(".bob{animation:bob 0.34s ease-in-out infinite;}")
    css.append(kf("legA", [(0, rot(-10, -28, 38)), (50, rot(-10, -28, -38)),
                           (100, rot(-10, -28, 38))]))
    css.append(".legA{animation:legA 0.34s ease-in-out infinite;}")
    css.append(".legB{animation:legA 0.34s ease-in-out -0.17s infinite;}")
    css.append(kf("armA", [(0, rot(14, -46, -40)), (50, rot(14, -46, 40)),
                           (100, rot(14, -46, -40))]))
    css.append(".armA{animation:armA 0.34s ease-in-out infinite;}")
    css.append(".armB{animation:armA 0.34s ease-in-out -0.17s infinite;}")
    css.append(kf("puff", [(0, "transform:translate(0,0) scale(0.3);opacity:0.85;"),
                           (100, "transform:translate(-30px,-10px) scale(1.7);opacity:0;")]))
    css.append(".puff{animation:puff 0.55s ease-out infinite;}")
    css.append(kf("leafw", [(0, "transform:translate(0,0) rotate(0deg);"),
                            (100, "transform:translate(-1040px,14px) rotate(-340deg);")]))
    css.append(".leafw{animation:leafw 2.2s linear infinite;}")

    o = ['<g class="runx"><g transform="translate(450,276)">']
    # dust puffs trailing the feet
    for i in range(3):
        o.append(f'<g class="puff" style="animation-delay:-{i * 0.18}s">'
                 + circle(-34 - i * 6, -6, 6 + i * 2, "#cdbfa3", 'opacity="0.8"')
                 + "</g>")
    o.append('<g class="bob">')
    # tail streaming behind
    o.append(limb("M-24,-40 q-22,2 -34,-14 q-8,-11 -2,-18", 7))
    # far limbs (drawn behind the body, darker)
    o.append('<g class="legB">' + limb("M-10,-28 Q-20,-12 -10,-3", 8.5, BODY_D) +
             ellipse(-9, -2, 7.5, 4, BODY_D) + "</g>")
    o.append('<g class="armB">' + limb("M14,-46 Q6,-32 14,-22", 7.5, BODY_D) +
             circle(14, -22, 4.4, BODY_D) + "</g>")
    # leaning body
    o.append(f'<g transform="rotate(-14)">{ellipse(0, -38, 29, 17, BODY)}'
             f'{ellipse(4, -34, 16, 9, CREAM)}</g>')
    # near limbs
    o.append('<g class="legA">' + limb("M-10,-28 Q-22,-14 -12,-2", 8.5) +
             ellipse(-11, -1, 8, 4.2, BODY_D) + "</g>")
    o.append('<g class="armA">' + limb("M14,-46 Q24,-32 18,-20", 7.5) +
             circle(18, -20, 4.6, BODY_D) + "</g>")
    o.append(head_svg(26, -56, 0.9, eyes="open", mouth="open", look=4.5))
    o.append("</g></g></g>")
    # leaves whooshing past (scene level, opposite direction feel)
    for i, (ly, s, dur, dl) in enumerate(((120, 1.0, 2.0, 0.0), (200, 0.8, 2.6, 0.9),
                                          (160, 1.2, 1.7, 1.5), (245, 0.7, 2.9, 0.4))):
        o.append(f'<g transform="translate(960,{ly}) scale({n(s)})">'
                 f'<g class="leafw" style="animation-duration:{n(dur)}s;'
                 f'animation-delay:-{n(dl)}s">'
                 f'<path d="M0,0 q8,-10 20,-8 q-4,12 -20,8 Z" fill="{pal["canopy3"]}"/>'
                 f"</g></g>")
    return "".join(o)


def scene_playing(css, pal):
    ax, ay = 450, 6
    css.append(kf("pend", [(0, rot(ax, ay, -38)), (50, rot(ax, ay, 38)),
                           (100, rot(ax, ay, -38))]))
    css.append(".pend{animation:pend 2.2s ease-in-out infinite;}")
    css.append(kf("pass2", [
        (0, "transform:translate(-130px,0);"),
        (46, "transform:translate(130px,0);"),
        (52, "transform:translate(130px,42px);"),
        (96, "transform:translate(-130px,42px);"),
        (100, "transform:translate(-130px,0);")]))
    css.append(".pass2{animation:pass2 8.8s ease-in-out infinite;}")
    css.append(kf("tailCurl", [(0, rot(14, 196, -8)), (50, rot(14, 196, 10)),
                               (100, rot(14, 196, -8))]))
    css.append(".tailCurl{animation:tailCurl 2.2s ease-in-out infinite;}")

    o = ['<g class="pass2"><g class="pend">']
    # the swing vine with leaf pairs
    o.append(limb(f"M{ax},{ay} q4,70 0,138", 4.5, "#3c6b35"))
    for vy in (40, 78, 112):
        o.append(f'<path d="M{ax},{vy} q-12,-3 -16,-12 q12,-2 16,12 Z" '
                 f'fill="{pal["canopy3"]}"/>')
        o.append(f'<path d="M{ax},{vy + 12} q12,-3 16,-12 q-12,-2 -16,12 Z" '
                 f'fill="{pal["canopy2"]}"/>')
    # Rohi gripping with both hands, body stretched, legs tucked
    mx = ax
    o.append(circle(mx - 5, 140, 4.8, BODY_D))
    o.append(circle(mx + 5, 143, 4.8, BODY_D))
    o.append(limb(f"M{mx - 5},140 Q{mx - 14},158 {mx - 8},170", 7.5))
    o.append(limb(f"M{mx + 5},143 Q{mx + 14},160 {mx + 8},170", 7.5))
    o.append(f'<g class="tailCurl">' +
             limb(f"M{mx + 4},206 q22,10 30,-6 q6,-13 -6,-16", 6.5) + "</g>")
    o.append(ellipse(mx, 196, 17, 25, BODY))
    o.append(ellipse(mx, 192, 10, 15, CREAM))
    o.append(head_svg(mx, 166, 0.92, eyes="happy", mouth="open"))
    # tucked legs, feet curled up
    o.append(limb(f"M{mx - 8},214 Q{mx - 20},222 {mx - 14},232", 8))
    o.append(ellipse(mx - 14, 233, 7, 4.2, BODY_D))
    o.append(limb(f"M{mx + 8},214 Q{mx + 20},222 {mx + 14},232", 8))
    o.append(ellipse(mx + 14, 233, 7, 4.2, BODY_D))
    o.append("</g></g>")
    return "".join(o)


def scene_fighting(css, pal):
    css.append(kf("lungeA", [
        (0, "transform:translate(0,0);"), (8, "transform:translate(52px,-6px);"),
        (16, "transform:translate(0,0);"), (50, "transform:translate(0,0);"),
        (58, "transform:translate(-28px,0) rotate(-6deg);"),
        (66, "transform:translate(0,0);"), (100, "transform:translate(0,0);")]))
    css.append(".lungeA{animation:lungeA 4s ease-in-out infinite;}")
    css.append(kf("lungeB", [
        (0, "transform:translate(0,0);"), (8, "transform:translate(-30px,0) rotate(-6deg);"),
        (16, "transform:translate(0,0);"), (50, "transform:translate(0,0);"),
        (58, "transform:translate(56px,-6px);"), (66, "transform:translate(0,0);"),
        (100, "transform:translate(0,0);")]))
    css.append(".lungeB{animation:lungeB 4s ease-in-out infinite;}")
    css.append(kf("dustC", [(0, scale_at(470, 252, 0.9, 0.9) + "opacity:0.45;"),
                            (50, scale_at(470, 252, 1.15, 1.05) + "opacity:0.8;"),
                            (100, scale_at(470, 252, 0.9, 0.9) + "opacity:0.45;")]))
    css.append(".dustC{animation:dustC 0.9s ease-in-out infinite;}")
    css.append(kf("pow", [
        (0, scale_at(470, 158, 0.1, 0.1) + "opacity:0;"),
        (7, scale_at(470, 158, 0.1, 0.1) + "opacity:0;"),
        (10, scale_at(470, 158, 1.25, 1.25) + "opacity:1;"),
        (14, scale_at(470, 158, 1, 1) + "opacity:1;"),
        (24, scale_at(470, 158, 0.5, 0.5) + "opacity:0;"),
        (57, scale_at(470, 158, 0.1, 0.1) + "opacity:0;"),
        (60, scale_at(470, 158, 1.25, 1.25) + "opacity:1;"),
        (64, scale_at(470, 158, 1, 1) + "opacity:1;"),
        (74, scale_at(470, 158, 0.5, 0.5) + "opacity:0;"),
        (100, scale_at(470, 158, 0.1, 0.1) + "opacity:0;")]))
    css.append(".pow{animation:pow 4s ease-out infinite;}")

    def fighter(body_c, cream_c, s):
        f = []
        f.append(ellipse(0, 1, 34, 6, "#000", 'opacity="0.18"'))
        f.append(tail_svg(-12, -28, flip=1, color=body_c))
        # crouched legs, wide stance
        f.append(limb("M-9,-24 Q-20,-12 -18,-2", 9, body_c))
        f.append(limb("M9,-24 Q20,-12 18,-2", 9, body_c))
        f.append(ellipse(-19, -1, 9, 4.5, BODY_D))
        f.append(ellipse(19, -1, 9, 4.5, BODY_D))
        f.append(ellipse(0, -42, 21, 26, body_c))
        f.append(ellipse(2, -38, 12, 16, cream_c))
        f.append(head_svg(6, -80, 0.95, eyes="open", mouth="grit", brows=True,
                          body=body_c))
        # guard arms with fists up
        f.append(limb("M14,-52 Q30,-52 30,-66", 8, body_c))
        f.append(circle(31, -69, 6, BODY_D))
        f.append(limb("M-12,-52 Q6,-44 16,-50", 8, body_c))
        f.append(circle(18, -51, 5.5, BODY_D))
        return "".join(f)

    o = []
    o.append(f'<g transform="translate(378,282)"><g class="lungeA">'
             + fighter(BODY, CREAM, 1.0) + "</g></g>")
    o.append(f'<g transform="translate(564,282) scale(-1.15,1.15)"><g class="lungeB">'
             + fighter(COUSIN, COUSIN_CREAM, 1.15) + "</g></g>")
    # comic dust cloud between them
    dust = ['<g class="dustC">']
    for dx, dy, dr in ((-26, 4, 13), (-8, -8, 16), (12, -2, 14), (28, 6, 11),
                       (0, 10, 15), (-18, 12, 10)):
        dust.append(circle(470 + dx, 252 + dy, dr, "#cdbfa3", 'opacity="0.55"'))
    dust.append("</g>")
    o.append("".join(dust))
    # POW! burst
    o.append('<g class="pow">'
             f'<path d="{star_path(470, 158, 10, 36, 18, 8)}" fill="#ffd23e" '
             f'stroke="#e2542a" stroke-width="3"/>'
             f'<text x="470" y="164" text-anchor="middle" font-size="17" '
             f'font-weight="800" fill="#b3271e" '
             f'font-family="{FAM}">POW!</text>'
             "</g>")
    return "".join(o)


SCENES = {
    "eating": scene_eating, "sleeping": scene_sleeping, "dancing": scene_dancing,
    "running": scene_running, "playing": scene_playing, "fighting": scene_fighting,
    "idle": scene_idle,
}


# ----------------------------------------------------------------------------
# environment layers
# ----------------------------------------------------------------------------


def sky_layer(pal, defs):
    c1, c2, c3 = pal["sky"]
    defs.append(f'<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1">'
                f'<stop offset="0" stop-color="{c1}"/>'
                f'<stop offset="0.55" stop-color="{c2}"/>'
                f'<stop offset="1" stop-color="{c3}"/></linearGradient>')
    return f'<rect width="{W}" height="{H}" fill="url(#sky)"/>'


def celestial_layer(pal, css):
    o = []
    kind = pal["celestial"]
    if kind == "sun":
        css.append(kf("sunspin", [(0, rot(585, 76, 0)), (100, rot(585, 76, 360))]))
        css.append(".sunspin{animation:sunspin 70s linear infinite;}")
        rays = ['<g class="sunspin">']
        for i in range(10):
            a = math.pi * 2 * i / 10
            x1 = 585 + 36 * math.cos(a)
            y1 = 76 + 36 * math.sin(a)
            x2 = 585 + 46 * math.cos(a)
            y2 = 76 + 46 * math.sin(a)
            rays.append(f'<line x1="{n(x1)}" y1="{n(y1)}" x2="{n(x2)}" y2="{n(y2)}" '
                        f'stroke="#ffe28a" stroke-width="3.5" stroke-linecap="round" '
                        f'opacity="0.85"/>')
        rays.append("</g>")
        o.append(circle(585, 76, 38, "#ffe9a0", 'opacity="0.45"'))
        o.append(circle(585, 76, 27, "#ffd75e"))
        o.append("".join(rays))
    elif kind == "dusksun":
        o.append(circle(585, 120, 42, "#ffb066", 'opacity="0.5"'))
        o.append(circle(585, 120, 30, "#ff8c42"))
    else:  # moon (kept low enough to clear the canopy)
        o.append(circle(540, 96, 26, "#f2efd9"))
        o.append(circle(551, 89, 22, pal["sky"][0]))
        o.append(circle(540, 96, 30, "#f2efd9", 'opacity="0.12"'))
    if pal["stars"]:
        css.append(kf("tw", [(0, "opacity:0.25;"), (50, "opacity:1;"),
                             (100, "opacity:0.25;")]))
        rng = _lcg(20260610)
        for i in range(26):
            sx = 16 + next(rng) * (W - 32)
            sy = 12 + next(rng) * 130
            sr = 0.7 + next(rng) * 1.1
            dur = 2.2 + next(rng) * 3.4
            dl = next(rng) * 4
            o.append(circle(sx, sy, sr, "#e9f1ff",
                            f'style="animation:tw {n(dur)}s ease-in-out -{n(dl)}s infinite"'))
    return "".join(o)


def firefly_layer(css):
    css.append(kf("ffl", [(0, "opacity:0.15;"), (50, "opacity:1;"),
                          (100, "opacity:0.15;")]))
    o = []
    rng = _lcg(937)
    for i in range(7):
        fx = 60 + next(rng) * 780
        fy = 150 + next(rng) * 110
        dx1, dy1 = (next(rng) - 0.5) * 70, (next(rng) - 0.5) * 44
        dx2, dy2 = (next(rng) - 0.5) * 70, (next(rng) - 0.5) * 44
        dur = 6 + next(rng) * 4
        name = f"fly{i}"
        css.append(kf(name, [
            (0, "transform:translate(0,0);"),
            (33, f"transform:translate({n(dx1)}px,{n(dy1)}px);"),
            (66, f"transform:translate({n(dx2)}px,{n(dy2)}px);"),
            (100, "transform:translate(0,0);")]))
        o.append(f'<g transform="translate({n(fx)},{n(fy)})">'
                 f'<g style="animation:{name} {n(dur)}s ease-in-out infinite">'
                 + circle(0, 0, 4.2, "#d9f76a", 'opacity="0.25"')
                 + circle(0, 0, 1.6, "#eaffa0",
                          f'style="animation:ffl {n(1.1 + i * 0.21)}s ease-in-out infinite"')
                 + "</g></g>")
    return "".join(o)


def canopy_layer(pal, css, with_swing_gap=False):
    css.append(kf("vsway", [(0, rot(0, 0, -2.2)), (50, rot(0, 0, 2.2)),
                            (100, rot(0, 0, -2.2))]))
    o = []
    back = [(60, 26, 150, 66), (255, 4, 150, 52), (700, 22, 170, 72), (875, 60, 150, 92)]
    mid = [(-10, 44, 120, 80), (165, 16, 125, 48), (830, 26, 150, 84), (645, 0, 110, 40)]
    front = [(-20, 76, 105, 76), (912, 92, 115, 86)]
    for cx, cy, rx, ry in back:
        o.append(ellipse(cx, cy, rx, ry, pal["canopy1"]))
    for cx, cy, rx, ry in mid:
        o.append(ellipse(cx, cy, rx, ry, pal["canopy2"]))
    for cx, cy, rx, ry in front:
        o.append(ellipse(cx, cy, rx, ry, pal["canopy3"], 'opacity="0.9"'))
    # hanging deco vines (skip middle one if the swing vine owns that space)
    vine_xs = (132, 790) if with_swing_gap else (132, 640, 790)
    for i, vx in enumerate(vine_xs):
        v = [f'<g transform="translate({vx},0)">'
             f'<g class="" style="animation:vsway {n(5 + i * 1.3)}s ease-in-out infinite">']
        v.append(limb("M0,0 q-7,52 4,96", 3.5, "#3c6b35"))
        for vy in (34, 64, 90):
            v.append(f'<path d="M{n(2 - vy / 30)},{vy} q-12,-2 -15,-11 q11,-2 15,11 Z" '
                     f'fill="{pal["canopy2"]}"/>')
        v.append("</g></g>")
        o.append("".join(v))
    return "".join(o)


def ground_layer(pal):
    o = [f'<rect x="0" y="270" width="{W}" height="50" fill="{pal["ground"]}"/>',
         f'<rect x="0" y="270" width="{W}" height="7" fill="{pal["ground2"]}"/>']
    rng = _lcg(4242)
    for i in range(14):
        gx = 14 + next(rng) * (W - 28)
        gy = 282 + next(rng) * 30
        o.append(f'<path d="M{n(gx)},{n(gy)} q2,-9 5,-11 M{n(gx + 5)},{n(gy)} q1,-7 6,-9" '
                 f'fill="none" stroke="{pal["moss"]}" stroke-width="1.6" '
                 f'stroke-linecap="round" opacity="0.7"/>')
    return "".join(o)


def log_layer(pal):
    o = []
    o.append(f'<rect x="158" y="238" width="190" height="40" rx="20" fill="{pal["log"]}"/>')
    o.append(ellipse(348, 258, 13, 20, pal["log2"]))
    o.append(ellipse(348, 258, 7, 11, pal["log"],
                     f'stroke="{pal["log2"]}" stroke-width="2"'))
    for bx in (190, 240, 295):
        o.append(f'<path d="M{bx},244 q14,4 30,2" fill="none" stroke="#000" '
                 f'stroke-width="1.5" opacity="0.15" stroke-linecap="round"/>')
    for mx, my, mr in ((185, 240, 12), (262, 238, 16), (322, 241, 10)):
        o.append(ellipse(mx, my, mr, 4.5, pal["moss"], 'opacity="0.85"'))
    return "".join(o)


# ----------------------------------------------------------------------------
# HUD
# ----------------------------------------------------------------------------


def hud_layer(state, css, defs, activity):
    def clamp(v):
        try:
            return max(0, min(100, int(v)))
        except (TypeError, ValueError):
            return 0

    bars = [("HUNGER", clamp(state.get("hunger")), "#ffb347"),
            ("ENERGY", clamp(state.get("energy")), "#4fc3f7"),
            ("HAPPY", clamp(state.get("happiness")), "#7ee081")]

    defs.append('<linearGradient id="shim" x1="0" y1="0" x2="1" y2="0">'
                '<stop offset="0" stop-color="#fff" stop-opacity="0"/>'
                '<stop offset="0.5" stop-color="#fff" stop-opacity="0.55"/>'
                '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
    css.append(kf("shimX", [(0, "transform:translate(-46px,0);"),
                            (55, "transform:translate(220px,0);"),
                            (100, "transform:translate(220px,0);")]))
    css.append(".shimX{animation:shimX 2.8s linear infinite;}")

    fam = FAM
    o = [f'<rect x="12" y="10" width="296" height="74" rx="12" fill="#000" opacity="0.28"/>',
         f'<rect x="690" y="10" width="198" height="106" rx="12" fill="#000" opacity="0.28"/>']
    track_x, track_w = 96, 168
    for i, (label, val, color) in enumerate(bars):
        y = 20 + i * 22
        fill_w = track_w * val / 100.0
        cp = f"barclip{i}"
        defs.append(f'<clipPath id="{cp}"><rect x="{track_x}" y="{y}" '
                    f'width="{n(fill_w)}" height="11" rx="5.5"/></clipPath>')
        o.append(f'<text x="24" y="{y + 9.5}" font-size="10" font-weight="700" '
                 f'fill="#fff" opacity="0.9" font-family="{fam}" '
                 f'letter-spacing="0.8">{label}</text>')
        o.append(f'<rect x="{track_x}" y="{y}" width="{track_w}" height="11" rx="5.5" '
                 f'fill="#fff" opacity="0.16"/>')
        o.append(f'<rect x="{track_x}" y="{y}" width="{n(fill_w)}" height="11" rx="5.5" '
                 f'fill="{color}"/>')
        o.append(f'<g clip-path="url(#{cp})"><rect x="{track_x - 46}" y="{y}" width="40" '
                 f'height="11" fill="url(#shim)" class="shimX" '
                 f'style="animation-delay:-{n(i * 0.5)}s"/></g>')
        o.append(f'<text x="{track_x + track_w + 6}" y="{y + 9.5}" font-size="10" '
                 f'fill="#fff" opacity="0.85" font-family="{fam}">{val}</text>')

    # right cluster: level badge, xp, bananas, wrestle record
    def _int(v):
        try:
            return int(v)
        except (TypeError, ValueError):
            return 0

    level = max(1, _int(state.get("level")) or 1)
    xp = _int(state.get("xp"))
    btoday = _int(state.get("bananas_today"))
    wins, losses = _int(state.get("wins")), _int(state.get("losses"))

    defs.append('<linearGradient id="gold" x1="0" y1="0" x2="0" y2="1">'
                '<stop offset="0" stop-color="#ffe082"/>'
                '<stop offset="1" stop-color="#f2a93b"/></linearGradient>')
    o.append('<rect x="702" y="20" width="76" height="26" rx="13" fill="url(#gold)" '
             'stroke="#b8860b" stroke-width="1"/>')
    o.append(f'<text x="740" y="38" text-anchor="middle" font-size="13" '
             f'font-weight="800" fill="#5a3a06" font-family="{fam}">LVL {level}</text>')
    o.append(f'<text x="876" y="38" text-anchor="end" font-size="12" font-weight="600" '
             f'fill="#fff" opacity="0.92" font-family="{fam}">XP {xp}</text>')
    o.append(banana_svg(714, 64, -28, 0.95))
    o.append(f'<text x="732" y="68" font-size="12" font-weight="600" fill="#fff" '
             f'opacity="0.92" font-family="{fam}">x {btoday} today</text>')
    o.append(f'<text x="702" y="94" font-size="11" font-weight="700" fill="#ffd9a0" '
             f'opacity="0.95" font-family="{fam}" letter-spacing="0.6">WRESTLING</text>')
    o.append(f'<text x="876" y="94" text-anchor="end" font-size="12" font-weight="700" '
             f'fill="#fff" font-family="{fam}">{wins}-{losses}</text>')
    return "".join(o)


def caption_layer(activity):
    text = CAPTIONS.get(activity, CAPTIONS["idle"])
    fam = FAM
    w = 36 + round(6.4 * len(text))
    return (f'<rect x="16" y="288" width="{w}" height="22" rx="11" fill="#000" '
            f'opacity="0.35"/>'
            + circle(30, 299, 3.5, "#7ee081")
            + f'<text x="40" y="303" font-size="11.5" font-weight="600" fill="#fff" '
              f'font-family="{fam}">{escape(text)}</text>')


# ----------------------------------------------------------------------------
# assembly
# ----------------------------------------------------------------------------


def build_svg(state: dict, activity: str, now: datetime) -> str:
    phase = sky_phase(now)
    pal = PALETTES[phase]
    css: list[str] = []
    defs: list[str] = [f'<clipPath id="frame"><rect width="{W}" height="{H}" rx="16"/>'
                       "</clipPath>"]
    layers: list[str] = []

    layers.append(sky_layer(pal, defs))
    layers.append(celestial_layer(pal, css))
    layers.append(canopy_layer(pal, css, with_swing_gap=(activity == "playing")))
    layers.append(ground_layer(pal))
    layers.append(log_layer(pal))
    layers.append(SCENES[activity](css, pal))
    if pal["fireflies"] or activity == "sleeping":
        layers.append(firefly_layer(css))
    layers.append(hud_layer(state, css, defs, activity))
    layers.append(caption_layer(activity))

    style = "".join(css)
    title = escape(f"Rohi the capuchin - {CAPTIONS.get(activity, activity)}")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
        f'width="{W}" height="{H}" role="img" aria-label="{title}">'
        f"<title>{title}</title>"
        f"<style>{style}</style>"
        f"<defs>{''.join(defs)}</defs>"
        f'<g clip-path="url(#frame)">{"".join(layers)}</g>'
        f'<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="16" fill="none" '
        f'stroke="#000" stroke-opacity="0.35" stroke-width="1"/>'
        f"</svg>"
    )


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="Render Rohi's animated SVG scene.")
    ap.add_argument("--state", required=True, help="path to rohi_state.json")
    ap.add_argument("--out", required=True, help="output SVG path")
    ap.add_argument("--activity", choices=ACTIVITIES, default=None,
                    help="override the activity stored in the state file")
    args = ap.parse_args(argv)

    state = load_state(args.state)
    activity = args.activity or state.get("activity") or "idle"
    if activity not in ACTIVITIES:
        print(f"render_rohi: unknown activity {activity!r}, falling back to idle",
              file=sys.stderr)
        activity = "idle"

    svg = build_svg(state, activity, now_charlotte())

    out_dir = os.path.dirname(os.path.abspath(args.out))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"render_rohi: wrote {args.out} "
          f"({len(svg.encode('utf-8'))} bytes, activity={activity})", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
