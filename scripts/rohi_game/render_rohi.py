#!/usr/bin/env python3
"""Rohi photo-composite renderer — cinematic photo + game HUD as ONE animated SVG.

The scene is one of the user's photos of Rohi, base64-embedded (GitHub's SVG
sanitizer blocks external refs), with a slow Ken Burns zoom/pan, per-activity
animated overlay effects, and a translucent game HUD composited on top.

Stdlib only. Safe for GitHub README <img> embedding:
  * no JavaScript, no external resources, system font stack only
  * animation is CSS @keyframes in <style> plus SMIL <animate>, looping forever

Usage:
    python3 scripts/rohi_game/render_rohi.py --state data/rohi_state.json \
        --out assets/rohi/rohi.svg [--activity dancing]

Env:
    ROHI_NOW="2026-06-10T21:00:00"  overrides the wall clock (deterministic
    tests). Naive timestamps are taken as America/New_York local time.
"""

from __future__ import annotations

import argparse
import base64
import json
import math
import os
import struct
import sys
from datetime import datetime
from xml.sax.saxutils import escape
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/New_York")
ASSET_DIR = os.path.normpath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "..", "assets", "rohi"))

ACTIVITIES = ("eating", "sleeping", "dancing", "running", "playing", "fighting", "idle")

# activity -> ordered photo candidates (first existing .jpg wins)
PHOTO_CHAIN = {
    "eating": ("eating",),
    "sleeping": ("sleeping",),
    "playing": ("playing",),
    "fighting": ("fighting",),
    "dancing": ("dancing", "playing"),
    "running": ("running", "playing"),
    "idle": ("idle", "sleeping"),
}
GLOBAL_FALLBACK = ("playing", "sleeping", "eating", "fighting")

# activity -> (zoom_to, pan_x, pan_y, duration_s) — slow documentary drift
KEN_BURNS = {
    "eating": (1.14, -40, -18, 22),
    "sleeping": (1.10, 30, -10, 28),
    "playing": (1.16, -55, -8, 20),
    "fighting": (1.15, 45, -15, 18),
    "dancing": (1.18, -30, -22, 19),
    "running": (1.16, 60, -10, 18),
    "idle": (1.10, 25, -12, 26),
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
PANEL = 'fill="#0d1117" fill-opacity="0.72"'  # rgba(13,17,23,0.72)
BANANA = "#ffd54a"
BANANA_EDGE = "#c79a2a"
REF_W = 900.0  # HUD design-space width; the HUD group is scaled to the photo

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


def scale_at(cx, cy, sx, sy, pre="") -> str:
    return (f"transform:{pre}translate({n(cx)}px,{n(cy)}px) scale({n(sx)},{n(sy)}) "
            f"translate({n(-cx)}px,{n(-cy)}px);")


def circle(cx, cy, r, fill, extra="") -> str:
    return f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="{fill}" {extra}/>'


def star_path(cx, cy, points, r1, r2, rot_deg=0.0) -> str:
    pts = []
    for i in range(points * 2):
        r = r1 if i % 2 == 0 else r2
        a = math.radians(rot_deg) + math.pi * i / points
        pts.append(f"{n(cx + r * math.sin(a))},{n(cy - r * math.cos(a))}")
    return "M" + " L".join(pts) + " Z"


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


def _lcg(seed: int):
    x = seed & 0x7FFFFFFF
    while True:
        x = (x * 1103515245 + 12345) & 0x7FFFFFFF
        yield x / 0x7FFFFFFF


# ----------------------------------------------------------------------------
# state / time / photo discovery
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


def find_photo(activity: str):
    """First existing .jpg from the activity's chain (then a global fallback)."""
    seen = set()
    for name in PHOTO_CHAIN[activity] + GLOBAL_FALLBACK:
        if name in seen:
            continue
        seen.add(name)
        path = os.path.join(ASSET_DIR, f"{name}.jpg")
        if os.path.isfile(path):
            return path, f"{name}.jpg"
    raise SystemExit(f"render_rohi: no photo available for {activity!r} in {ASSET_DIR}")


def jpeg_size(path):
    """Read width/height from JPEG headers (no deps)."""
    with open(path, "rb") as f:
        data = f.read()
    i = 2
    while i < len(data):
        if data[i] != 0xFF:
            i += 1
            continue
        marker = data[i + 1]
        if 0xC0 <= marker <= 0xCF and marker not in (0xC4, 0xC8, 0xCC):
            h, w = struct.unpack(">HH", data[i + 5: i + 9])
            return w, h
        i += 2 + struct.unpack(">H", data[i + 2: i + 4])[0]
    raise ValueError(f"no SOF marker in {path}")


# ----------------------------------------------------------------------------
# Ken Burns photo layer (SMIL, ported from build_rohi_motion.py)
# ----------------------------------------------------------------------------


def photo_layer(jpg_path: str, w: int, h: int, activity: str) -> str:
    zoom, px, py, dur = KEN_BURNS[activity]
    cx, cy = w / 2, h / 2
    # SMIL scale is around the origin; pre-scale translate keeps the zoom centred
    px = px + cx * (1 - zoom) / zoom
    py = py + cy * (1 - zoom) / zoom
    with open(jpg_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    return (
        '<g>'
        f'<animateTransform attributeName="transform" type="scale" '
        f'values="1;{n(zoom)};1" keyTimes="0;0.5;1" dur="{n(dur)}s" '
        f'calcMode="spline" keySplines="0.42 0 0.58 1;0.42 0 0.58 1" '
        f'repeatCount="indefinite"/>'
        '<g>'
        f'<animateTransform attributeName="transform" type="translate" '
        f'values="0,0;{n(px)},{n(py)};0,0" keyTimes="0;0.5;1" dur="{n(dur)}s" '
        f'calcMode="spline" keySplines="0.42 0 0.58 1;0.42 0 0.58 1" '
        f'repeatCount="indefinite"/>'
        f'<image href="data:image/jpeg;base64,{b64}" x="-{w * 0.06:.0f}" '
        f'y="-{h * 0.06:.0f}" width="{w * 1.12:.0f}" height="{h * 1.12:.0f}" '
        f'preserveAspectRatio="xMidYMid slice"/>'
        '</g></g>'
    )


# ----------------------------------------------------------------------------
# per-activity overlay effects (subtle; keep clear of the central face area)
# ----------------------------------------------------------------------------


def _smil_dust(w, h, k, spots=None):
    """Sun-dust motes drifting up (SMIL, ported from build_rohi_motion.py)."""
    spots = spots or [(0.2, 0.8), (0.32, 0.55), (0.52, 0.82), (0.68, 0.62),
                      (0.8, 0.7), (0.9, 0.45), (0.12, 0.4)]
    out = []
    for i, (fx, fy) in enumerate(spots):
        x, y = fx * w, fy * h
        r = (1.4 + (i % 3) * 0.5) * k
        out.append(
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{n(r)}" fill="#fff" opacity="0">'
            f'<animate attributeName="opacity" values="0;0.35;0" dur="{5 + i * 0.8:.1f}s" '
            f'begin="{i * 1.1:.1f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="cy" values="{y:.0f};{y - 60 * k:.0f}" dur="{9 + i:.0f}s" '
            f'begin="{i * 1.1:.1f}s" repeatCount="indefinite"/></circle>')
    return "".join(out)


def _smil_fireflies(w, h, k):
    """Fireflies (SMIL, ported from build_rohi_motion.py) — kept to the sides."""
    spots = [(0.13, 0.62), (0.27, 0.45), (0.6, 0.78), (0.74, 0.4), (0.88, 0.6), (0.34, 0.3)]
    out = []
    for i, (fx, fy) in enumerate(spots):
        x, y = fx * w, fy * h
        out.append(
            f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{n((2.5 + i % 2) * k)}" '
            f'fill="#e8ff9c" opacity="0">'
            f'<animate attributeName="opacity" values="0;0.9;0" dur="{3.5 + i * 0.7:.1f}s" '
            f'begin="{i * 1.3:.1f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="cy" values="{y:.0f};{y - 26 * k:.0f};{y:.0f}" '
            f'dur="{8 + i:.0f}s" repeatCount="indefinite"/>'
            f'<animate attributeName="cx" values="{x:.0f};{x + 14 * k:.0f};{x:.0f}" '
            f'dur="{6 + i:.0f}s" repeatCount="indefinite"/></circle>')
    return "".join(out)


def _ground_puffs(css, w, h, k, spots, drift=0.0):
    css.append(kf("puffB", [
        (0, f"transform:translate(0,0) scale(0.3);opacity:0;"),
        (25, "opacity:0.5;"),
        (100, f"transform:translate({n(drift * k)}px,{n(-8 * k)}px) scale(1.8);opacity:0;")]))
    css.append(".puffB{animation:puffB 1.6s ease-out infinite;transform-box:fill-box;"
               "transform-origin:center;}")
    out = []
    for i, (fx, fy) in enumerate(spots):
        out.append(f'<g class="puffB" style="animation-delay:-{n(i * 0.45)}s">'
                   + circle(fx * w, fy * h, (9 + (i % 3) * 3) * k, "#d8cdb4", 'opacity="0.5"')
                   + "</g>")
    return "".join(out)


def fx_eating(css, defs, w, h, k):
    return _smil_dust(w, h, k)


def fx_sleeping(css, defs, w, h, k):
    css.append(kf("zfloat", [
        (0, "opacity:0;transform:translate(0,0);"),
        (18, "opacity:1;"),
        (80, "opacity:0.9;"),
        (100, f"opacity:0;transform:translate({n(24 * k)}px,{n(-58 * k)}px);")]))
    css.append(".zfloat{animation:zfloat 4.8s ease-out infinite;}")
    o = [_smil_fireflies(w, h, k)]
    zx, zy = 0.16 * w, 0.46 * h
    for i, (dx, dy, fs, dl) in enumerate(((0, 0, 15, 0.0), (13, -14, 20, 1.6),
                                          (28, -30, 26, 3.2))):
        o.append(f'<text x="{n(zx + dx * k)}" y="{n(zy + dy * k)}" font-family="{FAM}" '
                 f'font-size="{n(fs * k)}" font-style="italic" font-weight="700" '
                 f'fill="#dfe9ff" class="zfloat" style="animation-delay:-{n(dl)}s">z</text>')
    return "".join(o)


def fx_playing(css, defs, w, h, k):
    css.append(kf("leafFall", [
        (0, "transform:translate(0,0) rotate(0deg);opacity:0;"),
        (5, "opacity:0.9;"),
        (30, f"transform:translate({n(-30 * k)}px,{n(0.36 * h)}px) rotate(120deg);opacity:0.9;"),
        (58, f"transform:translate({n(20 * k)}px,{n(0.72 * h)}px) rotate(260deg);opacity:0.85;"),
        (70, f"transform:translate({n(-6 * k)}px,{n(0.96 * h)}px) rotate(330deg);opacity:0;"),
        (100, f"transform:translate({n(-6 * k)}px,{n(0.96 * h)}px) rotate(330deg);opacity:0;")]))
    css.append(".leafFall{animation:leafFall 9s linear infinite;}")
    leaf = (f'<g transform="translate({n(0.84 * w)},{n(-0.04 * h)})"><g class="leafFall">'
            f'<path transform="scale({n(1.5 * k)})" d="M0,0 q10,-12 24,-10 q-5,14 -24,10 Z" '
            f'fill="#7bb661" opacity="0.9"/></g></g>')
    return _smil_dust(w, h, k) + leaf


def fx_fighting(css, defs, w, h, k):
    o = [_ground_puffs(css, w, h, k,
                       [(0.22, 0.9), (0.32, 0.94), (0.66, 0.92), (0.8, 0.95)])]
    px, py = 0.78 * w, 0.3 * h
    css.append(kf("pow6", [
        (0, scale_at(px, py, 0.1, 0.1) + "opacity:0;"),
        (3, scale_at(px, py, 0.1, 0.1) + "opacity:0;"),
        (6, scale_at(px, py, 1.25, 1.25) + "opacity:1;"),
        (10, scale_at(px, py, 1, 1) + "opacity:1;"),
        (18, scale_at(px, py, 0.5, 0.5) + "opacity:0;"),
        (100, scale_at(px, py, 0.1, 0.1) + "opacity:0;")]))
    css.append(".pow6{animation:pow6 6s ease-out infinite;}")
    o.append('<g class="pow6">'
             f'<path d="{star_path(px, py, 10, 40 * k, 20 * k, 8)}" fill="#ffd23e" '
             f'stroke="#e2542a" stroke-width="{n(3 * k)}"/>'
             f'<text x="{n(px)}" y="{n(py + 6 * k)}" text-anchor="middle" '
             f'font-size="{n(19 * k)}" font-weight="800" fill="#b3271e" '
             f'font-family="{FAM}">POW!</text></g>')
    return "".join(o)


def fx_dancing(css, defs, w, h, k):
    # party glow vignette: two coloured edge glows cross-fading (colour shift)
    for gid, col in (("pgPink", "#ff5fa8"), ("pgBlue", "#4fc3f7")):
        defs.append(f'<radialGradient id="{gid}" cx="0.5" cy="0.5" r="0.72">'
                    f'<stop offset="0.55" stop-color="{col}" stop-opacity="0"/>'
                    f'<stop offset="1" stop-color="{col}" stop-opacity="0.4"/>'
                    f'</radialGradient>')
    css.append(kf("glowP", [(0, "opacity:0.06;"), (50, "opacity:0.55;"),
                            (100, "opacity:0.06;")]))
    css.append(".glowP{animation:glowP 7s ease-in-out infinite;}")
    o = [f'<rect width="{w}" height="{h}" fill="url(#pgPink)" class="glowP"/>',
         f'<rect width="{w}" height="{h}" fill="url(#pgBlue)" class="glowP" '
         f'style="animation-delay:-3.5s"/>']
    # music notes bouncing up along the sides
    css.append(kf("noteR", [
        (0, "transform:translate(0,0);opacity:0;"),
        (12, "opacity:0.95;"),
        (55, f"transform:translate({n(10 * k)}px,{n(-0.3 * h)}px);opacity:0.9;"),
        (100, f"transform:translate({n(-6 * k)}px,{n(-0.55 * h)}px);opacity:0;")]))
    css.append(".noteR{animation:noteR 5s ease-out infinite;}")
    notes = ((0.06, 0.78, 2.6, "#ffe9a8"), (0.11, 0.88, 3.2, "#ffc1e3"),
             (0.89, 0.84, 2.3, "#bde0ff"), (0.94, 0.74, 3.0, "#ffe9a8"))
    for i, (fx, fy, s, col) in enumerate(notes):
        o.append(f'<g class="noteR" style="animation-delay:-{n(i * 1.25)}s">'
                 + note_svg(fx * w, fy * h, s * k, col) + "</g>")
    return "".join(o)


def fx_running(css, defs, w, h, k):
    line_w = 0.24 * w
    css.append(kf("speedX", [
        (0, "transform:translate(0,0);"),
        (100, f"transform:translate({n(-(w + line_w))}px,0);")]))
    o = []
    for i, fy in enumerate((0.16, 0.3, 0.46, 0.64, 0.82)):
        o.append(f'<g style="animation:speedX {n(1.1 + i * 0.22)}s linear '
                 f'-{n(i * 0.37)}s infinite">'
                 f'<rect x="{n(w)}" y="{n(fy * h)}" width="{n(line_w)}" '
                 f'height="{n(3.2 * k)}" rx="{n(1.6 * k)}" fill="#fff" '
                 f'opacity="0.35"/></g>')
    o.append(_ground_puffs(css, w, h, k, [(0.3, 0.92), (0.52, 0.95), (0.72, 0.93)],
                           drift=-26))
    return "".join(o)


def fx_idle(css, defs, w, h, k):
    css.append(kf("twk", [(0, "opacity:0.1;"), (50, "opacity:0.9;"),
                          (100, "opacity:0.1;")]))
    o = []
    rng = _lcg(20260610)
    placed = 0
    while placed < 14:
        fx, fy = next(rng), next(rng) * 0.34
        r = (0.9 + next(rng) * 1.3) * k
        dur, dl = 2.2 + next(rng) * 3.2, next(rng) * 4
        if 0.36 < fx < 0.64 and fy > 0.15:  # keep the centre clear
            continue
        o.append(circle(fx * w, fy * h, r, "#f3f7ff",
                        f'style="animation:twk {n(dur)}s ease-in-out -{n(dl)}s infinite"'))
        placed += 1
    # one slow shooting star streaking from the top-right
    defs.append('<linearGradient id="shoot" x1="0" y1="0" x2="1" y2="0">'
                '<stop offset="0" stop-color="#fff" stop-opacity="0.9"/>'
                '<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
    css.append(kf("shootS", [
        (0, "transform:translate(0,0);opacity:0;"),
        (84, "transform:translate(0,0);opacity:0;"),
        (88, "opacity:0.9;"),
        (100, f"transform:translate({n(-0.42 * w)}px,0);opacity:0;")]))
    o.append(f'<g transform="translate({n(0.88 * w)},{n(0.09 * h)}) rotate(-16)">'
             f'<g style="animation:shootS 11s linear infinite">'
             f'<rect x="0" y="0" width="{n(0.09 * w)}" height="{n(2.4 * k)}" '
             f'rx="{n(1.2 * k)}" fill="url(#shoot)"/></g></g>')
    return "".join(o)


OVERLAYS = {
    "eating": fx_eating, "sleeping": fx_sleeping, "playing": fx_playing,
    "fighting": fx_fighting, "dancing": fx_dancing, "running": fx_running,
    "idle": fx_idle,
}


# ----------------------------------------------------------------------------
# HUD (bars + shimmer ported from the previous sprite renderer)
# ----------------------------------------------------------------------------


def hud_layer(state, css, defs):
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
    o = [f'<rect x="12" y="10" width="296" height="74" rx="12" {PANEL}/>',
         f'<rect x="690" y="10" width="198" height="106" rx="12" {PANEL}/>']
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


def caption_layer(activity, design_h):
    text = CAPTIONS.get(activity, CAPTIONS["idle"])
    fam = FAM
    wc = 36 + round(6.4 * len(text))
    y = design_h - 34
    return (f'<rect x="16" y="{n(y)}" width="{wc}" height="22" rx="11" {PANEL}/>'
            + circle(30, y + 11, 3.5, "#7ee081")
            + f'<text x="40" y="{n(y + 15)}" font-size="11.5" font-weight="600" '
              f'fill="#fff" font-family="{fam}">{escape(text)}</text>')


# ----------------------------------------------------------------------------
# assembly
# ----------------------------------------------------------------------------


def build_svg(state: dict, activity: str, now: datetime) -> tuple[str, str]:
    jpg_path, photo_name = find_photo(activity)
    w, h = jpeg_size(jpg_path)
    k = w / REF_W                 # HUD design-space scale
    design_h = h / k

    css: list[str] = []
    defs: list[str] = [f'<clipPath id="frame"><rect width="{w}" height="{h}" rx="{n(18 * k)}"/>'
                       "</clipPath>",
                       '<radialGradient id="vig" cx="0.5" cy="0.5" r="0.75">'
                       '<stop offset="0.62" stop-color="#000" stop-opacity="0"/>'
                       '<stop offset="1" stop-color="#000" stop-opacity="0.32"/>'
                       '</radialGradient>']

    layers = [photo_layer(jpg_path, w, h, activity)]
    layers.append(OVERLAYS[activity](css, defs, w, h, k))
    layers.append(f'<rect width="{w}" height="{h}" fill="url(#vig)"/>')
    layers.append(f'<g transform="scale({n(k)})">'
                  + hud_layer(state, css, defs)
                  + caption_layer(activity, design_h)
                  + "</g>")

    title = escape(f"Rohi the capuchin - {CAPTIONS.get(activity, activity)} - "
                   f"{now.strftime('%-I:%M %p')} in Charlotte", {'"': "&quot;"})
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" '
        f'width="{w}" height="{h}" role="img" aria-label="{title}">'
        f"<title>{title}</title>"
        f"<style>{''.join(css)}</style>"
        f"<defs>{''.join(defs)}</defs>"
        f'<g clip-path="url(#frame)">{"".join(layers)}</g>'
        f"</svg>"
    )
    return svg, f"{photo_name} {w}x{h}"


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

    svg, photo_info = build_svg(state, activity, now_charlotte())

    out_dir = os.path.dirname(os.path.abspath(args.out))
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as fh:
        fh.write(svg)
    print(f"render_rohi: wrote {args.out} "
          f"({len(svg.encode('utf-8'))} bytes, activity={activity}, photo={photo_info})",
          file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
