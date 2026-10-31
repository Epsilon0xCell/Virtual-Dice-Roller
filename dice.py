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

# I anchor this at both ends so a half written form like 3d6+ or 3d6++2
# fails outright instead of matching the good half and rolling anyway.
# The sign rides inside the modifier group, which is why int() on that
# group below needs no sign handling of its own. IGNORECASE is there for
# 3D6, which I type often enough that rejecting it would just annoy me.
PATTERN = re.compile(r"^(?:(\d*)d(\d+)|(\d+))([+-]\d+)?$", re.IGNORECASE)


def parse(expr):
    """Parse a dice expression into (count, sides, modifier). Raise ValueError."""
    # I strip only the outside. An inner space, as in 3d6 +5, still fails
    # the match, and I prefer that to quietly guessing what was meant.
    m = PATTERN.match(expr.strip())
    if not m:
        raise ValueError("invalid dice notation: {!r} (try 3d6, d20, 2d10+3)".format(expr))
    if m.group(3) is not None:
        # A bare number means that many d6 in my notation. Six is a choice
        # I baked in here, not something the input states.
        count, sides = int(m.group(3)), 6
    else:
        # An empty first group is the d20 shorthand: no count typed, so 1.
        count = int(m.group(1)) if m.group(1) else 1
        sides = int(m.group(2))
    modifier = int(m.group(4)) if m.group(4) else 0
    # I bound count and sides here, after the parse and before any roll.
    # Count sets how long the rolls list gets in roll(), and sides sets
    # the randint range, so these two are the inputs I do not let through
    # unchecked. The modifier is bounded just below, for a different
    # reason: it cannot break the roll, only produce a silly total.
    if count < 1 or count > 1000:
        raise ValueError("dice count must be between 1 and 1000")
    if sides < 2 or sides > 10000:
        raise ValueError("dice sides must be between 2 and 10000")
    # The modifier gets a bound too, as of this pass. Count and sides were
    # capped from the start, but the modifier slipped through unchecked:
    # 3d6+999999999999 parsed and printed a total over a trillion, which is
    # a typo shape, not a roll anyone means. A million is far past any
    # modifier a real game uses, so nothing honest is lost by capping it.
    if abs(modifier) > 1000000:
        raise ValueError("modifier must be between -1000000 and 1000000")
    return count, sides, modifier


def roll(expr, rng=random):
    """Roll a dice expression. Return (rolls, modifier, total)."""
    # rng is either the random module or a random.Random instance, and I
    # rely on both having randint with the same call shape. That split is
    # what lets main() hand in a seeded Random without roll() caring.
    count, sides, modifier = parse(expr)
    rolls = [rng.randint(1, sides) for _ in range(count)]
    return rolls, modifier, sum(rolls) + modifier


def describe(expr, rolls, modifier, total):
    dice = ", ".join(str(r) for r in rolls)
    # {:+d} forces the sign onto the modifier. Without it a line like
    # [4, 1] 5 = 10 reads as a third die, and I want the printed line to
    # show the same shape the user typed. Zero prints nothing extra.
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
        # I store the modifier in the tuple because the total alone cannot
        # rebuild the printed line. Storing only expr, rolls, and total
        # was the bug that made history list a 2d20+5 roll as [4, 1] = 10
        # with the +5 nowhere on the line. stats() below unpacks this
        # same four part shape, so the two have to change together.
        self.history.append((expr, rolls, modifier, total))
        return describe(expr, rolls, modifier, total)

    def stats(self):
        if not self.history:
            return "No rolls yet."
        # Totals here are the finished totals, modifier included. The dice
        # count is a separate sum over the rolls lists, so a 2d20+5 entry
        # counts as 2 dice and a total of 10 at the same time.
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
            # EOF falls out of the loop instead of returning here so the
            # stats line after the loop still prints. Quit lands there
            # too. If I returned on EOF, a closed pipe would end the
            # session with no summary at all.
            print()
            break
        except KeyboardInterrupt:
            # Ctrl-C gets the same clean exit as EOF. Before this, it
            # escaped input() as a traceback and the session ended with
            # no stats line, which made an ordinary way of leaving look
            # like a crash.
            print()
            break
        if not raw:
            continue
        # Commands are checked before I try to roll, off a lowered copy.
        # The copy means HISTORY works, and passing raw, not cmd, to
        # do_roll below keeps the case the user typed in the printed line
        # and in history, so 3D6 stays 3D6.
        cmd = raw.lower()
        if cmd in ("quit", "exit", "q"):
            break
        if cmd == "stats":
            print(session.stats())
            continue
        if cmd == "history":
            if not session.history:
                print("No rolls yet.")
            # I print history through describe() instead of rebuilding a
            # line here, so a history line can never drift from the line
            # the roll printed when it happened. That drift already bit
            # me once, with the missing modifier.
            for expr, rolls, modifier, total in session.history:
                print("  " + describe(expr, rolls, modifier, total))
            continue
        # A bad expression in this mode prints and the prompt comes back.
        # That is the opposite choice from batch mode in main(), and it
        # is deliberate: one typo should not throw away a whole session.
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
    # I test the seed against None, not for truth. Seed 0 is a real seed
    # a user can ask for, and a plain if args.seed would drop it and roll
    # unseeded while claiming nothing was wrong.
    rng = random.Random(args.seed) if args.seed is not None else random
    if not args.expressions:
        interactive(rng)
        return 0
    # Batch mode stops at the first bad expression and returns 2. Rolls
    # already printed stay printed and later expressions never roll. I
    # want a script using this to fail loudly instead of getting a
    # shorter set of results that looks complete.
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
