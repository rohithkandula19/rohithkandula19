#!/usr/bin/env python3
"""One-time builder: wrap each Rohi photo in a cinematic motion SVG.

Ken Burns documentary effect — slow zoom + pan over the embedded photo
(base64; GitHub's SVG sanitizer blocks external refs), plus scene-matched
particles: fireflies on the night shot, drifting sun-dust on day shots.
Output: assets/rohi/<scene>.svg alongside each .jpg. Stdlib only.
"""
import base64
import os
import struct

DIR = os.path.join(os.path.dirname(__file__), "..", "assets", "rohi")

# scene -> (zoom_to, pan_x, pan_y, duration_s, particles)
MOTION = {
    "eating": (1.14, -40, -18, 22, "dust"),
    "sleeping": (1.10, 30, -10, 28, "fireflies"),
    "playing": (1.16, -55, -8, 20, "dust"),
    "fighting": (1.15, 45, -15, 18, "dust"),
}


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
            h, w = struct.unpack(">HH", data[i + 5 : i + 9])
            return w, h
        i += 2 + struct.unpack(">H", data[i + 2 : i + 4])[0]
    raise ValueError(f"no SOF marker in {path}")


def particles(kind, w, h):
    out = []
    if kind == "fireflies":
        spots = [(0.15, 0.62), (0.32, 0.45), (0.55, 0.7), (0.7, 0.4), (0.85, 0.6), (0.45, 0.3)]
        for i, (fx, fy) in enumerate(spots):
            x, y = fx * w, fy * h
            out.append(
                f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{2.5 + i % 2}" fill="#e8ff9c" opacity="0">'
                f'<animate attributeName="opacity" values="0;0.9;0" dur="{3.5 + i * 0.7:.1f}s" '
                f'begin="{i * 1.3:.1f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="cy" values="{y:.0f};{y - 26:.0f};{y:.0f}" '
                f'dur="{8 + i:.0f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="cx" values="{x:.0f};{x + 14:.0f};{x:.0f}" '
                f'dur="{6 + i:.0f}s" repeatCount="indefinite"/></circle>'
            )
    else:  # sun-dust motes drifting up through the light
        spots = [(0.2, 0.8), (0.35, 0.55), (0.52, 0.75), (0.66, 0.5), (0.8, 0.7), (0.9, 0.45), (0.12, 0.4)]
        for i, (fx, fy) in enumerate(spots):
            x, y = fx * w, fy * h
            out.append(
                f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{1.4 + (i % 3) * 0.5:.1f}" fill="#fff" opacity="0">'
                f'<animate attributeName="opacity" values="0;0.35;0" dur="{5 + i * 0.8:.1f}s" '
                f'begin="{i * 1.1:.1f}s" repeatCount="indefinite"/>'
                f'<animate attributeName="cy" values="{y:.0f};{y - 60:.0f}" dur="{9 + i:.0f}s" '
                f'begin="{i * 1.1:.1f}s" repeatCount="indefinite"/></circle>'
            )
    return "".join(out)


def build(scene):
    jpg = os.path.join(DIR, f"{scene}.jpg")
    w, h = jpeg_size(jpg)
    with open(jpg, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    zoom, px, py, dur, pkind = MOTION[scene]
    cx, cy = w / 2, h / 2
    # SMIL scale is around the origin; pre-scale translate keeps the zoom centred
    px = px + cx * (1 - zoom) / zoom
    py = py + cy * (1 - zoom) / zoom

    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {w} {h}" width="{w}" height="{h}" role="img" aria-label="Rohi — {scene}">
  <defs>
    <radialGradient id="vig" cx="0.5" cy="0.5" r="0.75">
      <stop offset="0.62" stop-color="#000" stop-opacity="0"/>
      <stop offset="1" stop-color="#000" stop-opacity="0.32"/>
    </radialGradient>
    <clipPath id="frame"><rect width="{w}" height="{h}" rx="18"/></clipPath>
  </defs>
  <g clip-path="url(#frame)">
    <g>
      <animateTransform attributeName="transform" type="scale"
        values="1;{zoom};1" keyTimes="0;0.5;1" dur="{dur}s"
        calcMode="spline" keySplines="0.42 0 0.58 1;0.42 0 0.58 1"
        repeatCount="indefinite"/>
      <g>
        <animateTransform attributeName="transform" type="translate"
          values="0,0;{px},{py};0,0" keyTimes="0;0.5;1" dur="{dur}s"
          calcMode="spline" keySplines="0.42 0 0.58 1;0.42 0 0.58 1"
          repeatCount="indefinite"/>
        <image href="data:image/jpeg;base64,{b64}" x="-{w * 0.06:.0f}" y="-{h * 0.06:.0f}"
          width="{w * 1.12:.0f}" height="{h * 1.12:.0f}" preserveAspectRatio="xMidYMid slice"/>
      </g>
    </g>
    {particles(pkind, w, h)}
    <rect width="{w}" height="{h}" fill="url(#vig)"/>
  </g>
</svg>"""
    out = os.path.join(DIR, f"{scene}.svg")
    with open(out, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"{scene}.svg — {os.path.getsize(out) // 1024} KB ({w}x{h}, {dur}s loop, {pkind})")


def main():
    for scene in MOTION:
        build(scene)


if __name__ == "__main__":
    main()
