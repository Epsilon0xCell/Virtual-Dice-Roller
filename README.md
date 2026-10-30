# Virtual-Dice-Roller

A dice roller in Python. Roll standard dice notation from the command line or
in an interactive session with history and statistics.

## Notation

| Expression | Meaning                        |
|------------|--------------------------------|
| `3d6`      | roll 3 six-sided dice          |
| `d20`      | roll 1 twenty-sided die        |
| `2d20+5`   | roll 2d20 and add 5            |
| `1d8-1`    | roll 1d8 and subtract 1        |
| `4`        | roll 4 six-sided dice          |

Limits: 1-1000 dice, 2-10000 sides.

## Run

```sh
python3 dice.py 3d6            # single roll
python3 dice.py 2d20+5 1d8     # several rolls at once
python3 dice.py --seed 42 4d6  # reproducible rolls
python3 dice.py                # interactive mode
```

Example output:

```
3d6: [6, 1, 1] = 8
2d20+5: [9, 8] +5 = 22
```

## Interactive mode

Run with no arguments. Type any dice expression to roll it. Commands:

- `history` - list every roll this session
- `stats` - count, min, max, average and total across the session
- `quit` - exit (prints final stats)

## License

MIT (see LICENSE).
