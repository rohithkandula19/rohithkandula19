#!/usr/bin/env python3
"""Issue-driven Connect 4: visitors are Red, a minimax bot is Yellow.

Triggered by the Connect 4 workflow on issues titled `c4|drop|<1-7>` or
`c4|new`. Run locally with ISSUE_TITLE=init to (re)render only. Stdlib only.
"""
import json
import math
import os
import random
import re
import urllib.parse

ROOT = os.path.join(os.path.dirname(__file__), "..")
GAME_DIR = os.path.join(ROOT, "games", "connect4")
STATE_FILE = os.path.join(GAME_DIR, "state.json")
LOG_FILE = os.path.join(GAME_DIR, "moves.log")
SVG_FILE = os.path.join(GAME_DIR, "board.svg")
COMMENT_FILE = os.path.join(GAME_DIR, "comment.txt")
README = os.path.join(ROOT, "README.md")
REPO = "rohithkandula19/rohithkandula19"

ROWS, COLS = 6, 7
EMPTY, RED, YELLOW = 0, 1, 2  # visitor = RED, bot = YELLOW
BOT_DEPTH = 4
HISTORY_SHOWN = 10
DIGITS = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣"]


def comment(text):
    with open(COMMENT_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")


def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE, encoding="utf-8") as f:
            return json.load(f)
    return {"grid": [[EMPTY] * COLS for _ in range(ROWS)], "over": False, "result": ""}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(state, f)


def log_move(line):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def recent_moves():
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()][-HISTORY_SHOWN:]


def issue_url(title):
    q = urllib.parse.quote(title, safe="")
    body = urllib.parse.quote("Just press 'Create' — the bot does the rest.", safe="")
    return f"https://github.com/{REPO}/issues/new?title={q}&body={body}"


def drop(grid, col, piece):
    """Place piece in col; returns row or None if column full."""
    for row in range(ROWS - 1, -1, -1):
        if grid[row][col] == EMPTY:
            grid[row][col] = piece
            return row
    return None


def windows(grid):
    for r in range(ROWS):
        for c in range(COLS):
            if c + 3 < COLS:
                yield [grid[r][c + i] for i in range(4)]
            if r + 3 < ROWS:
                yield [grid[r + i][c] for i in range(4)]
            if c + 3 < COLS and r + 3 < ROWS:
                yield [grid[r + i][c + i] for i in range(4)]
            if c - 3 >= 0 and r + 3 < ROWS:
                yield [grid[r + i][c - i] for i in range(4)]


def winner(grid):
    for w in windows(grid):
        if w[0] != EMPTY and all(x == w[0] for x in w):
            return w[0]
    return None


def full(grid):
    return all(grid[0][c] != EMPTY for c in range(COLS))


def score(grid, piece):
    opp = RED if piece == YELLOW else YELLOW
    s = sum(2 for r in range(ROWS) if grid[r][COLS // 2] == piece)
    for w in windows(grid):
        mine, theirs = w.count(piece), w.count(opp)
        if theirs == 0:
            s += {4: 1000, 3: 8, 2: 2}.get(mine, 0)
        elif mine == 0:
            s -= {4: 1000, 3: 10, 2: 2}.get(theirs, 0)
    return s


def legal_cols(grid):
    return [c for c in range(COLS) if grid[0][c] == EMPTY]


def minimax(grid, depth, alpha, beta, maximizing):
    win = winner(grid)
    if win == YELLOW:
        return None, 10_000 + depth
    if win == RED:
        return None, -10_000 - depth
    if full(grid) or depth == 0:
        return None, score(grid, YELLOW)
    cols = sorted(legal_cols(grid), key=lambda c: abs(c - COLS // 2))
    best_col = cols[0]
    if maximizing:
        value = -math.inf
        for c in cols:
            g = [row[:] for row in grid]
            drop(g, c, YELLOW)
            _, v = minimax(g, depth - 1, alpha, beta, False)
            if v > value:
                value, best_col = v, c
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return best_col, value
    value = math.inf
    for c in cols:
        g = [row[:] for row in grid]
        drop(g, c, RED)
        _, v = minimax(g, depth - 1, alpha, beta, True)
        if v < value:
            value, best_col = v, c
        beta = min(beta, value)
        if alpha >= beta:
            break
    return best_col, value


def bot_move(grid):
    cols = legal_cols(grid)
    if not cols:
        return None
    # tiny chance of a casual move so the bot stays beatable
    if random.random() < 0.12:
        return random.choice(cols)
    col, _ = minimax(grid, BOT_DEPTH, -math.inf, math.inf, True)
    return col


def render_svg(grid, last=None):
    cell, pad = 56, 14
    w = pad * 2 + COLS * cell
    h = pad * 2 + ROWS * cell
    discs = []
    for r in range(ROWS):
        for c in range(COLS):
            cx = pad + c * cell + cell / 2
            cy = pad + r * cell + cell / 2
            v = grid[r][c]
            if v == EMPTY:
                discs.append(f'<circle cx="{cx}" cy="{cy}" r="21" fill="#0d1117"/>')
                continue
            color = "#f85149" if v == RED else "#e3b341"
            if last == (r, c):
                discs.append(
                    f'<circle cx="{cx}" cy="{cy}" r="21" fill="{color}">'
                    f'<animate attributeName="cy" from="-24" to="{cy}" dur="0.6s" '
                    f'calcMode="spline" keySplines="0.3 0 0.6 1" fill="freeze"/></circle>'
                )
            else:
                discs.append(f'<circle cx="{cx}" cy="{cy}" r="21" fill="{color}"/>')
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}">'
        f'<rect x="0" y="0" width="{w}" height="{h}" rx="14" fill="#1f6feb"/>'
        + "".join(discs)
        + "</svg>"
    )
    with open(SVG_FILE, "w", encoding="utf-8") as f:
        f.write(svg)


def render_readme(state, note=""):
    cols_open = legal_cols(state["grid"]) if not state["over"] else []
    drops = "  ".join(
        f"[{DIGITS[c]}]({issue_url(f'c4|drop|{c + 1}')})" if c in cols_open else DIGITS[c]
        for c in range(COLS)
    )
    history = recent_moves()
    history_md = (
        "  \n".join(f"<sub>{m}</sub>" for m in history)
        if history
        else "<sub>No moves yet — drop the first disc!</sub>"
    )
    block = f"""
<div align="center">

**🔴 Connect 4 — you vs my bot.** You're **Red**, the bot is **Yellow**. One click = one move: pick a column below → a pre-filled GitHub issue opens → press *Create* → a GitHub Action drops your disc, the bot replies, and this board re-renders.

<img src="games/connect4/board.svg" width="320" alt="connect 4 board"/>

**Drop your disc:**&nbsp;&nbsp;{drops}

{note}

<details><summary>Recent moves</summary>

{history_md}

</details>

<sub>[🔄 Start a new game]({issue_url('c4|new')}) · played entirely with GitHub issues + Actions</sub>

</div>
"""
    with open(README, encoding="utf-8") as f:
        text = f.read()
    text = re.sub(
        r"(<!-- CONNECT4:START -->)(.*?)(<!-- CONNECT4:END -->)",
        lambda m: m.group(1) + block + m.group(3),
        text,
        flags=re.DOTALL,
    )
    with open(README, "w", encoding="utf-8") as f:
        f.write(text)


def main():
    os.makedirs(GAME_DIR, exist_ok=True)
    open(COMMENT_FILE, "w").close()
    title = os.environ.get("ISSUE_TITLE", "init").strip()
    author = os.environ.get("ISSUE_AUTHOR", "someone")
    state = load_state()
    grid = state["grid"]

    if title == "init":
        save_state(state)
        render_svg(grid)
        render_readme(state)
        return

    parts = [p.strip() for p in title.split("|")]
    cmd = parts[1] if len(parts) > 1 else ""

    if cmd == "new":
        state = {"grid": [[EMPTY] * COLS for _ in range(ROWS)], "over": False, "result": ""}
        save_state(state)
        open(LOG_FILE, "w").close()
        render_svg(state["grid"])
        render_readme(state, note="🆕 **Fresh board — new game started.**")
        comment("New game started — Red (you) moves first. Thanks for playing!")
        return

    if cmd != "drop" or len(parts) < 3 or not parts[2].isdigit():
        comment("I couldn't parse that. Use an issue title like `c4|drop|4` (columns 1-7).")
        return

    col = int(parts[2]) - 1
    if not 0 <= col < COLS:
        comment("Columns are 1-7 — pick one of the links on my profile!")
        return

    if state["over"]:
        # courtesy: a drop on a finished game starts a fresh one
        state = {"grid": [[EMPTY] * COLS for _ in range(ROWS)], "over": False, "result": ""}
        grid = state["grid"]
        open(LOG_FILE, "w").close()

    row = drop(grid, col, RED)
    if row is None:
        comment(f"Column {col + 1} is full — pick another one!")
        return
    log_move(f"🔴 column {col + 1} — @{author}")
    last = (row, col)
    note, bot_col = "", None

    if winner(grid) == RED:
        state["over"], state["result"] = True, "red"
        note = f"🏆 **Red wins — the internet beat the bot!** [Rematch?]({issue_url('c4|new')})"
    elif full(grid):
        state["over"], state["result"] = True, "draw"
        note = f"🤝 **Draw — the board is full.** [Rematch?]({issue_url('c4|new')})"
    else:
        bot_col = bot_move(grid)
        if bot_col is not None:
            bot_row = drop(grid, bot_col, YELLOW)
            log_move(f"🟡 column {bot_col + 1} — bot")
            last = (bot_row, bot_col)
            if winner(grid) == YELLOW:
                state["over"], state["result"] = True, "yellow"
                note = f"🤖 **Yellow wins — the bot takes this one.** [Rematch?]({issue_url('c4|new')})"
            elif full(grid):
                state["over"], state["result"] = True, "draw"
                note = f"🤝 **Draw — the board is full.** [Rematch?]({issue_url('c4|new')})"

    save_state(state)
    render_svg(grid, last=last)
    render_readme(state, note=note)
    msg = f"You dropped in column **{col + 1}**."
    if bot_col is not None:
        msg += f" The bot replied in column **{bot_col + 1}**."
    comment(msg + f" The [board](https://github.com/{REPO}) is updated — your move!")


if __name__ == "__main__":
    main()
