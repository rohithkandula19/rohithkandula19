#!/usr/bin/env python3
"""Issue-driven chess: visitors play White vs a Stockfish bot on the profile README.

Triggered by the Chess workflow when an issue titled `chess|move|<SAN>` or
`chess|new` is opened. Run locally with ISSUE_TITLE=init to (re)render only.
"""
import os
import re
import shutil
import urllib.parse

import chess
import chess.engine
import chess.svg

ROOT = os.path.join(os.path.dirname(__file__), "..")
GAME_DIR = os.path.join(ROOT, "games", "chess")
FEN_FILE = os.path.join(GAME_DIR, "state.fen")
LOG_FILE = os.path.join(GAME_DIR, "moves.log")
SVG_FILE = os.path.join(GAME_DIR, "board.svg")
COMMENT_FILE = os.path.join(GAME_DIR, "comment.txt")
README = os.path.join(ROOT, "README.md")
REPO = "rohithkandula19/rohithkandula19"

MAX_MOVE_LINKS = 24
HISTORY_SHOWN = 10


def comment(text: str) -> None:
    with open(COMMENT_FILE, "a", encoding="utf-8") as f:
        f.write(text + "\n")


def load_board() -> chess.Board:
    if os.path.exists(FEN_FILE):
        with open(FEN_FILE, encoding="utf-8") as f:
            return chess.Board(f.read().strip())
    return chess.Board()


def save_board(board: chess.Board) -> None:
    with open(FEN_FILE, "w", encoding="utf-8") as f:
        f.write(board.fen())


def log_move(line: str) -> None:
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line + "\n")


def recent_moves() -> list[str]:
    if not os.path.exists(LOG_FILE):
        return []
    with open(LOG_FILE, encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()][-HISTORY_SHOWN:]


def issue_url(title: str) -> str:
    q = urllib.parse.quote(title, safe="")
    body = urllib.parse.quote("Just press 'Create' — the bot does the rest.", safe="")
    return f"https://github.com/{REPO}/issues/new?title={q}&body={body}"


def render(board: chess.Board, note: str = "") -> None:
    lastmove = board.peek() if board.move_stack else None
    with open(SVG_FILE, "w", encoding="utf-8") as f:
        f.write(chess.svg.board(board, lastmove=lastmove, size=420))

    legal = sorted(board.san(m) for m in board.legal_moves)[:MAX_MOVE_LINKS]
    links = " · ".join(f"[`{san}`]({issue_url('chess|move|' + san)})" for san in legal)
    history = recent_moves()
    history_md = (
        "  \n".join(f"<sub>{h}</sub>" for h in history)
        if history
        else "<sub>No moves yet — make the first one!</sub>"
    )

    block = f"""
<div align="center">

**♟️ Play chess against my profile.** You (the internet) are **White**; a Stockfish bot is **Black**.
Click a move → a pre-filled GitHub issue opens → press *Create* → a GitHub Action plays it, gets Stockfish's reply, and re-renders this board.

<img src="games/chess/board.svg" width="420" alt="chess board"/>

{note}

**Your move:** {links}

<details><summary>Recent moves</summary>

{history_md}

</details>

<sub>Any legal move works: open an issue titled <code>chess|move|&lt;SAN&gt;</code> (e.g. <code>chess|move|Nf3</code>) · [Start a new game]({issue_url('chess|new')})</sub>

</div>
"""
    with open(README, encoding="utf-8") as f:
        text = f.read()
    text = re.sub(
        r"(<!-- CHESS:START -->)(.*?)(<!-- CHESS:END -->)",
        lambda m: m.group(1) + block + m.group(3),
        text,
        flags=re.DOTALL,
    )
    with open(README, "w", encoding="utf-8") as f:
        f.write(text)


def engine_reply(board: chess.Board) -> chess.Move | None:
    path = shutil.which("stockfish") or "/usr/games/stockfish"
    if not (shutil.which("stockfish") or os.path.exists(path)):
        return None
    engine = chess.engine.SimpleEngine.popen_uci(path)
    try:
        # beatable on purpose — nobody plays twice against a wall
        engine.configure({"Skill Level": 5})
        return engine.play(board, chess.engine.Limit(time=0.5)).move
    finally:
        engine.quit()


def main() -> None:
    os.makedirs(GAME_DIR, exist_ok=True)
    open(COMMENT_FILE, "w").close()
    title = os.environ.get("ISSUE_TITLE", "init").strip()
    author = os.environ.get("ISSUE_AUTHOR", "someone")
    board = load_board()

    if title == "init":
        save_board(board)
        render(board)
        return

    parts = [p.strip() for p in title.split("|")]
    cmd = parts[1] if len(parts) > 1 else ""

    if cmd == "new":
        board = chess.Board()
        save_board(board)
        open(LOG_FILE, "w").close()
        render(board, note="🆕 **Fresh board — new game started.**")
        comment("New game started — White to move. Thanks for playing!")
        return

    if cmd != "move" or len(parts) < 3 or not parts[2]:
        comment("I couldn't parse that. Use an issue title like `chess|move|e4`.")
        return

    raw = parts[2]
    move = None
    try:
        move = board.parse_san(raw)
    except ValueError:
        try:
            candidate = chess.Move.from_uci(raw.lower())
            if candidate in board.legal_moves:
                move = candidate
        except ValueError:
            move = None
    if move is None or move not in board.legal_moves:
        comment(
            f"`{raw}` isn't a legal move in the current position. "
            f"Pick one of the move links on [my profile](https://github.com/{REPO})!"
        )
        return

    san = board.san(move)
    board.push(move)
    log_move(f"⚪ {san} — @{author}")

    note = ""
    reply_san = None
    if board.is_game_over():
        note = (
            f"🏁 **Game over: {board.result()}** · "
            f"[Start a new game]({issue_url('chess|new')})"
        )
    else:
        reply = engine_reply(board)
        if reply is not None:
            reply_san = board.san(reply)
            board.push(reply)
            log_move(f"⚫ {reply_san} — Stockfish")
            if board.is_game_over():
                note = (
                    f"🏁 **Game over: {board.result()}** · "
                    f"[Start a new game]({issue_url('chess|new')})"
                )

    save_board(board)
    render(board, note=note)
    msg = f"You played **{san}**."
    if reply_san:
        msg += f" Stockfish replied **{reply_san}**."
    comment(msg + f" The [board](https://github.com/{REPO}) is updated — your move!")


if __name__ == "__main__":
    main()
