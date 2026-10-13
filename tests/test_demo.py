"""Demo reproducibility, episode boundaries, and CLI validation."""

from contextlib import redirect_stdout
import io
import unittest
from unittest.mock import patch

import demo


class DemoTests(unittest.TestCase):
    def test_real_multi_episode_demo_is_repeatable(self):
        outputs = []
        for _ in range(2):
            output = io.StringIO()
            with redirect_stdout(output):
                demo.main(["--episodes", "2", "--render-mode", "ansi"])
            outputs.append(output.getvalue())
        self.assertEqual(outputs[0], outputs[1])
        lines = outputs[0].splitlines()
        self.assertEqual(len(lines), 43)  # Header, two summaries, two 20-row grids.
        self.assertIn("Episode 1:", lines[1])
        self.assertIn("Episode 2:", lines[22])
        for summary in (lines[1], lines[22]):
            self.assertTrue("terminated=True" in summary or "truncated=True" in summary)

    def test_stops_on_either_flag_and_closes(self):
        for flags in ((True, False), (False, True), (True, True)):
            with patch("demo.gym.make") as make:
                env = make.return_value.__enter__.return_value
                env.reset.return_value = (380, {})
                env.step.return_value = (19, 100.0, *flags, {"steps": 1, "position": (0, 19)})
                with redirect_stdout(io.StringIO()):
                    demo.main(["--episodes", "2"])
                self.assertEqual(env.step.call_count, 2)
                self.assertEqual(env.reset.call_args_list[0].kwargs, {"seed": 123})
                self.assertEqual(env.reset.call_args_list[1].kwargs, {"seed": None})
                env.action_space.seed.assert_called_once_with(456)
                make.return_value.__exit__.assert_called_once()

    def test_invalid_cli_arguments(self):
        for args in (["--episodes", "0"], ["--seed", "-1"],
                     ["--action-seed", "-1"], ["--render-mode", "rgb_array"]):
            with patch("sys.stderr", new=io.StringIO()), self.assertRaises(SystemExit) as error:
                demo.main(args)
            self.assertEqual(error.exception.code, 2)
