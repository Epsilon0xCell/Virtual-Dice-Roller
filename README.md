![Virtual Dice Roller banner](banner.png)

# Virtual-Dice-Roller

A dice roller in Python. Roll standard dice notation from the command line or
in an interactive session with history and statistics.

Requirements: Python 3, standard library only.

## Notation

| Expression | Meaning                        |
|------------|--------------------------------|
| `3d6`      | roll 3 six-sided dice          |
| `d20`      | roll 1 twenty-sided die        |
| `2d20+5`   | roll 2d20 and add 5            |
| `1d8-1`    | roll 1d8 and subtract 1        |
| `4`        | roll 4 six-sided dice          |

Limits: 1 to 1000 dice, 2 to 10000 sides. An expression outside those limits
or in any other format is rejected with an error message.

## Run

```sh
python3 dice.py 3d6            # single roll
python3 dice.py 2d20+5 1d8     # several rolls at once
python3 dice.py --seed 42 4d6  # reproducible rolls
python3 dice.py                # interactive mode
```

Verified example with a fixed seed:

```sh
$ python3 dice.py --seed 42 4d6 2d20+5 1d8-1
4d6: [6, 1, 1, 6] = 14
2d20+5: [9, 8] +5 = 22
1d8-1: [4] -1 = 3
```

In batch mode, rolls are printed in order. If an expression is invalid, the
program prints `Error: ...` to stderr, stops, and exits with status 2. Rolls
already printed before the bad expression stay printed.

## Interactive mode

Run with no arguments. Type any dice expression to roll it. Commands:

- `history` - list every roll this session, with modifiers shown
- `stats` - count, min, max, average and total across the session
- `quit`, `exit`, or `q` - exit (prints final stats)

An invalid expression in interactive mode prints an error and the session
continues. Typing `history` or `stats` before any roll prints
`No rolls yet.` Closing input (EOF) ends the session and prints the final
stats. Exit status is 0.

## Files

- `dice.py` - the whole program
- `logo.png`, `banner.png` - project branding
- `LICENSE` - MIT license

## License

MIT (see LICENSE).
