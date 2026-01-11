#!/usr/bin/env python3
import curses
import time
from typing import Iterable, List, Set, Tuple

Cell = Tuple[int, int]


def parse_pattern(lines: Iterable[str], live_char: str = "O") -> List[Cell]:
    cells: List[Cell] = []
    for r, line in enumerate(lines):
        for c, ch in enumerate(line):
            if ch == live_char:
                cells.append((r, c))
    return cells


def normalize_cells(cells: Iterable[Cell]) -> List[Cell]:
    rows = [r for r, _ in cells]
    cols = [c for _, c in cells]
    if not rows or not cols:
        return []
    min_r = min(rows)
    min_c = min(cols)
    return [(r - min_r, c - min_c) for r, c in cells]


def seed_pattern(cells: Iterable[Cell], rows: int, cols: int) -> Set[Cell]:
    normalized = normalize_cells(cells)
    if not normalized:
        return set()
    max_r = max(r for r, _ in normalized)
    max_c = max(c for _, c in normalized)
    height = max_r + 1
    width = max_c + 1
    offset_r = max(0, (rows - height) // 2)
    offset_c = max(0, (cols - width) // 2)
    live: Set[Cell] = set()
    for r, c in normalized:
        rr = r + offset_r
        cc = c + offset_c
        if 0 <= rr < rows and 0 <= cc < cols:
            live.add((rr, cc))
    return live


def step(live: Set[Cell], rows: int, cols: int) -> Set[Cell]:
    counts = {}
    for r, c in live:
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                rr = r + dr
                cc = c + dc
                if 0 <= rr < rows and 0 <= cc < cols:
                    counts[(rr, cc)] = counts.get((rr, cc), 0) + 1
    next_live: Set[Cell] = set()
    for cell, neighbors in counts.items():
        if neighbors == 3 or (neighbors == 2 and cell in live):
            next_live.add(cell)
    return next_live


def draw(stdscr: "curses._CursesWindow", live: Set[Cell], rows: int, cols: int) -> None:
    blank = " " * cols
    rows_to_cols = {}
    for r, c in live:
        rows_to_cols.setdefault(r, []).append(c)

    for r in range(rows):
        if r in rows_to_cols:
            row = [" "] * cols
            for c in rows_to_cols[r]:
                if 0 <= c < cols:
                    row[c] = "O"
            line = "".join(row)
        else:
            line = blank
        try:
            stdscr.addstr(r, 0, line)
        except curses.error:
            pass
    stdscr.refresh()


def run(stdscr: "curses._CursesWindow") -> None:
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.keypad(True)

    patterns = [
        {
            "name": "Gosper Glider Gun",
            "cells": [
                (0, 4), (0, 5), (1, 4), (1, 5),
                (10, 4), (10, 5), (10, 6),
                (11, 3), (11, 7),
                (12, 2), (12, 8),
                (13, 2), (13, 8),
                (14, 5),
                (15, 3), (15, 7),
                (16, 4), (16, 5), (16, 6),
                (17, 5),
                (20, 2), (20, 3), (20, 4),
                (21, 2), (21, 3), (21, 4),
                (22, 1), (22, 5),
                (24, 0), (24, 1), (24, 5), (24, 6),
                (34, 2), (34, 3), (35, 2), (35, 3),
            ],
        },
        {
            "name": "Pulsar",
            "cells": parse_pattern(
                [
                    "..OOO...OOO..",
                    ".............",
                    "O....O.O....O",
                    "O....O.O....O",
                    "O....O.O....O",
                    "..OOO...OOO..",
                    ".............",
                    "..OOO...OOO..",
                    "O....O.O....O",
                    "O....O.O....O",
                    "O....O.O....O",
                    ".............",
                    "..OOO...OOO..",
                ]
            ),
        },
        {
            "name": "Acorn",
            "cells": [
                (0, 1), (1, 3), (2, 0), (2, 1), (2, 4), (2, 5), (2, 6)
            ],
        },
        {
            "name": "Lightweight Spaceship",
            "cells": parse_pattern(
                [
                    ".O..O",
                    "O....",
                    "O...O",
                    "OOOO.",
                ]
            ),
        },
    ]

    pattern_index = 0
    rows, cols = stdscr.getmaxyx()
    live = seed_pattern(patterns[pattern_index]["cells"], rows, cols)
    seen_states = set()

    while True:
        rows_now, cols_now = stdscr.getmaxyx()
        if (rows_now, cols_now) != (rows, cols):
            rows, cols = rows_now, cols_now
            live = seed_pattern(patterns[pattern_index]["cells"], rows, cols)
            seen_states.clear()

        draw(stdscr, live, rows, cols)

        key = stdscr.getch()
        if key in (ord("q"), ord("Q")):
            break
        if key in (ord("n"), ord("N")):
            pattern_index = (pattern_index + 1) % len(patterns)
            live = seed_pattern(patterns[pattern_index]["cells"], rows, cols)
            seen_states.clear()

        state_hash = hash(frozenset(live))
        if state_hash in seen_states or not live:
            pattern_index = (pattern_index + 1) % len(patterns)
            live = seed_pattern(patterns[pattern_index]["cells"], rows, cols)
            seen_states.clear()
            continue

        seen_states.add(state_hash)
        live = step(live, rows, cols)
        time.sleep(0.05)


def main() -> None:
    curses.wrapper(run)


if __name__ == "__main__":
    main()
