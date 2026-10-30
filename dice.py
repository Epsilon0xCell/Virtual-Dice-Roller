#!/usr/bin/env python3
"""Virtual Dice Roller: roll dice from the command line or an interactive prompt.

Notation:
    NdS         roll N dice with S sides        (e.g. 3d6)
    NdS+M       add a modifier                  (e.g. 2d20+5)
    NdS-M       subtract a modifier             (e.g. 1d8-1)
    dS          shorthand for 1dS               (e.g. d20)
    N           a plain number rolls that many d6

Usage:
    python3 dice.py 3d6
    python3 dice.py 2d20+5 1d8
    python3 dice.py --seed 42 4d6     # reproducible rolls
    python3 dice.py                   # interactive mode with history/stats
"""

import argparse
import random
import re
import sys

PATTERN = re.compile(r"^(?:(\d*)d(\d+)|(\d+))([+-]\d+)?$", re.IGNORECASE)


def parse(expr):
    """Parse a dice expression into (count, sides, modifier). Raise ValueError."""
    m = PATTERN.match(expr.strip())
    if not m:
        raise ValueError("invalid dice notation: {!r} (try 3d6, d20, 2d10+3)".format(expr))
    if m.group(3) is not None:
        count, sides = int(m.group(3)), 6
    else:
        count = int(m.group(1)) if m.group(1) else 1
        sides = int(m.group(2))
    modifier = int(m.group(4)) if m.group(4) else 0
    if count < 1 or count > 1000:
        raise ValueError("dice count must be between 1 and 1000")
    if sides < 2 or sides > 10000:
        raise ValueError("dice sides must be between 2 and 10000")
    return count, sides, modifier


def roll(expr, rng=random):
    """Roll a dice expression. Return (rolls, modifier, total)."""
    count, sides, modifier = parse(expr)
    rolls = [rng.randint(1, sides) for _ in range(count)]
    return rolls, modifier, sum(rolls) + modifier


def describe(expr, rolls, modifier, total):
    dice = ", ".join(str(r) for r in rolls)
    if modifier:
        return "{}: [{}] {:+d} = {}".format(expr, dice, modifier, total)
    return "{}: [{}] = {}".format(expr, dice, total)


class Session:
    """Tracks history and statistics for interactive mode."""

    def __init__(self, rng=random):
        self.rng = rng
        self.history = []

    def do_roll(self, expr):
        rolls, modifier, total = roll(expr, self.rng)
        self.history.append((expr, rolls, modifier, total))
        return describe(expr, rolls, modifier, total)

    def stats(self):
        if not self.history:
            return "No rolls yet."
        totals = [t for _, _, _, t in self.history]
        dice = sum(len(r) for _, r, _, _ in self.history)
        return ("Rolls: {} expressions, {} dice | min {} | max {} | "
                "average {:.2f} | total {}".format(
                    len(self.history), dice, min(totals), max(totals),
                    sum(totals) / len(totals), sum(totals)))


def interactive(rng=random):
    session = Session(rng)
    print("Virtual Dice Roller. Enter dice notation (e.g. 3d6, d20, 2d10+3).")
    print("Commands: stats, history, quit")
    while True:
        try:
            raw = input("roll> ").strip()
        except EOFError:
            print()
            break
        if not raw:
            continue
        cmd = raw.lower()
        if cmd in ("quit", "exit", "q"):
            break
        if cmd == "stats":
            print(session.stats())
            continue
        if cmd == "history":
            if not session.history:
                print("No rolls yet.")
            for expr, rolls, modifier, total in session.history:
                print("  " + describe(expr, rolls, modifier, total))
            continue
        try:
            print(session.do_roll(raw))
        except ValueError as exc:
            print("Error: {}".format(exc))
    print(session.stats())


def main(argv=None):
    parser = argparse.ArgumentParser(description="Virtual dice roller (NdN notation).")
    parser.add_argument("expressions", nargs="*", help="dice expressions, e.g. 3d6 2d20+5")
    parser.add_argument("--seed", type=int, default=None,
                        help="seed the RNG for reproducible rolls")
    args = parser.parse_args(argv)
    rng = random.Random(args.seed) if args.seed is not None else random
    if not args.expressions:
        interactive(rng)
        return 0
    for expr in args.expressions:
        try:
            rolls, modifier, total = roll(expr, rng)
        except ValueError as exc:
            print("Error: {}".format(exc), file=sys.stderr)
            return 2
        print(describe(expr, rolls, modifier, total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
