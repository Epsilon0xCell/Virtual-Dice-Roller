"""Tests for dice.py. Run with: python3 -m unittest"""

import io
import random
import unittest
from unittest import mock

import dice


class ParseTests(unittest.TestCase):
    def test_valid_forms(self):
        self.assertEqual(dice.parse("3d6"), (3, 6, 0))
        self.assertEqual(dice.parse("d20"), (1, 20, 0))
        self.assertEqual(dice.parse("2d20+5"), (2, 20, 5))
        self.assertEqual(dice.parse("1d8-1"), (1, 8, -1))
        self.assertEqual(dice.parse("4"), (4, 6, 0))
        self.assertEqual(dice.parse("3D6"), (3, 6, 0))
        # Leading zeros parse as the number they name.
        self.assertEqual(dice.parse("007d6"), (7, 6, 0))

    def test_invalid_forms(self):
        for bad in ("foo", "3d6+", "d", "-3d6", "3.5d6", "", "3d6++2",
                    "3d6 +5"):
            with self.assertRaises(ValueError, msg=bad):
                dice.parse(bad)

    def test_count_and_sides_bounds(self):
        for bad in ("0d6", "1001d6", "3d1", "3d10001"):
            with self.assertRaises(ValueError, msg=bad):
                dice.parse(bad)

    def test_modifier_bound(self):
        self.assertEqual(dice.parse("3d6+1000000"), (3, 6, 1000000))
        self.assertEqual(dice.parse("3d6-1000000"), (3, 6, -1000000))
        with self.assertRaises(ValueError):
            dice.parse("3d6+1000001")
        with self.assertRaises(ValueError):
            dice.parse("3d6+999999999999")


class RollTests(unittest.TestCase):
    def test_seeded_roll_matches_readme(self):
        rng = random.Random(42)
        self.assertEqual(dice.roll("4d6", rng), ([6, 1, 1, 6], 0, 14))
        self.assertEqual(dice.roll("2d20+5", rng), ([9, 8], 5, 22))
        self.assertEqual(dice.roll("1d8-1", rng), ([4], -1, 3))

    def test_negative_total_is_allowed(self):
        # A modifier can pull a total below zero (1d2-5). The README
        # states this instead of the code silently clamping it.
        rolls, modifier, total = dice.roll("1d2-5", random.Random(1))
        self.assertEqual(total, sum(rolls) - 5)
        self.assertLess(total, 0)

    def test_describe(self):
        self.assertEqual(dice.describe("2d20+5", [4, 1], 5, 10),
                         "2d20+5: [4, 1] +5 = 10")
        self.assertEqual(dice.describe("3d6", [1, 2, 3], 0, 6),
                         "3d6: [1, 2, 3] = 6")


class SessionTests(unittest.TestCase):
    def test_history_and_stats(self):
        s = dice.Session(random.Random(42))
        line = s.do_roll("2d20+5")
        self.assertIn("+5", line)
        self.assertIn("Rolls: 1 expressions, 2 dice", s.stats())
        self.assertEqual(len(s.history), 1)

    def test_empty_stats(self):
        self.assertEqual(dice.Session().stats(), "No rolls yet.")


class MainTests(unittest.TestCase):
    def run_main(self, argv):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch("sys.stdout", out), mock.patch("sys.stderr", err):
            code = dice.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_batch_ok(self):
        code, out, _ = self.run_main(["--seed", "42", "4d6"])
        self.assertEqual(code, 0)
        self.assertIn("4d6: [6, 1, 1, 6] = 14", out)

    def test_batch_seed_zero_is_a_real_seed(self):
        code1, out1, _ = self.run_main(["--seed", "0", "3d6"])
        code2, out2, _ = self.run_main(["--seed", "0", "3d6"])
        self.assertEqual((code1, code2), (0, 0))
        self.assertEqual(out1, out2)

    def test_batch_bad_expression_stops_with_2(self):
        code, out, err = self.run_main(["--seed", "1", "3d6", "BAD", "2d6"])
        self.assertEqual(code, 2)
        self.assertIn("Error", err)
        self.assertNotIn("2d6:", out)

    def test_batch_modifier_over_bound_exits_2(self):
        code, _, err = self.run_main(["3d6+999999999999"])
        self.assertEqual(code, 2)
        self.assertIn("modifier", err)


class InteractiveTests(unittest.TestCase):
    def run_interactive(self, fake_input):
        out = io.StringIO()
        with mock.patch("builtins.input", fake_input), \
                mock.patch("sys.stdout", out):
            dice.interactive(random.Random(42))
        return out.getvalue()

    def test_eof_prints_final_stats(self):
        def fake_input(prompt=""):
            raise EOFError
        out = self.run_interactive(fake_input)
        self.assertIn("No rolls yet.", out)

    def test_ctrl_c_prints_final_stats_without_traceback(self):
        def fake_input(prompt=""):
            raise KeyboardInterrupt
        out = self.run_interactive(fake_input)
        self.assertIn("No rolls yet.", out)

    def test_roll_history_stats_quit(self):
        answers = iter(["2d20+5", "history", "stats", "quit"])
        out = self.run_interactive(lambda prompt="": next(answers))
        self.assertIn("2d20+5: [4, 1] +5 = 10", out)
        # The history line repeats the roll line, modifier included.
        self.assertEqual(out.count("2d20+5: [4, 1] +5 = 10"), 2)
        self.assertIn("Rolls: 1 expressions, 2 dice", out)

    def test_bad_expression_does_not_end_session(self):
        answers = iter(["nope", "3d6", "quit"])
        out = self.run_interactive(lambda prompt="": next(answers))
        self.assertIn("Error:", out)
        self.assertIn("Rolls: 1 expressions", out)


if __name__ == "__main__":
    unittest.main()
