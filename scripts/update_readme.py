#!/usr/bin/env python3
"""Refresh the live-status board and recently-shipped feed in README.md.

Runs in GitHub Actions on a 6-hour cron (and on demand). Stdlib only.
"""
import json
import os
import re
import time
import urllib.request
from datetime import datetime, timezone

README = os.path.join(os.path.dirname(__file__), "..", "README.md")
USER = "rohithkandula19"

LIVE_APPS = [
    ("RO MedRAG", "https://romedrag.me"),
    ("BullshiftDetector", "https://bullshiftdetector.web.app"),
    ("MR Buses", "https://mrbusportal.com"),
    ("RO Fraud Detection", "https://rover-ai.duckdns.org"),
]

UA = {"User-Agent": "profile-refresh/1.0 (+https://github.com/rohithkandula19)"}


def ping(url: str) -> tuple[str, str]:
    start = time.monotonic()
    try:
        req = urllib.request.Request(url, headers=UA)
        with urllib.request.urlopen(req, timeout=15) as resp:
            ms = int((time.monotonic() - start) * 1000)
            if resp.status < 400:
                badge = "🟢 LIVE" if ms < 3000 else "🟡 SLOW"
                return badge, f"{ms} ms"
            return "🔴 DOWN", f"HTTP {resp.status}"
    except Exception:
        return "🔴 DOWN", "n/a"


def gh_api(path: str):
    req = urllib.request.Request(f"https://api.github.com{path}", headers=dict(UA))
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.load(resp)


def status_table() -> str:
    rows = ["| System | Status | Response |", "|---|---|---|"]
    for name, url in LIVE_APPS:
        badge, latency = ping(url)
        host = url.split("//", 1)[1]
        rows.append(f"| [{name}]({url}) | {badge} | {latency} |")
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    rows.append("")
    rows.append(f"<sub>🤖 Checked automatically every 6 hours by GitHub Actions · last run {stamp}</sub>")
    return "\n".join(rows)


def shipped_list() -> str:
    repos = gh_api(f"/users/{USER}/repos?sort=pushed&per_page=30")
    lines = []
    for r in repos:
        if r.get("fork") or r["name"] == USER:
            continue
        pushed = r["pushed_at"][:10]
        desc = (r.get("description") or "").strip().replace("\u2014", "\u00b7")
        if len(desc) > 90:
            desc = desc[:87] + "…"
        suffix = f" · {desc}" if desc else ""
        lines.append(f"- **[{r['name']}]({r['html_url']})** · pushed {pushed}{suffix}")
        if len(lines) == 5:
            break
    return "\n".join(lines)


def splice(text: str, marker: str, new: str) -> str:
    pattern = re.compile(
        rf"(<!-- {marker}:START -->)(.*?)(<!-- {marker}:END -->)", re.DOTALL
    )
    if not pattern.search(text):
        raise SystemExit(f"missing markers for {marker}")
    return pattern.sub(rf"\1\n{new}\n\3", text)


def main() -> None:
    with open(README, encoding="utf-8") as f:
        text = f.read()
    text = splice(text, "STATUS", status_table())
    text = splice(text, "SHIPPED", shipped_list())
    with open(README, "w", encoding="utf-8") as f:
        f.write(text)
    print("README refreshed.")


if __name__ == "__main__":
    main()
