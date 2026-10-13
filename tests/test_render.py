"""Text dimensions, symbols, human output, and rendering side effects."""

from contextlib import redirect_stdout
import copy
import io
import unittest

from icy_gridworld import goal, obstacles
from icy_gridworld.env import IcyGridWorldEnv


class RenderTests(unittest.TestCase):
    def test_every_traversable_agent_position(self):
        env = IcyGridWorldEnv(render_mode="ansi")
        env.reset(seed=0)
        for r in range(20):
            for c in range(20):
                if (r, c) in obstacles:
                    continue
                env._position = (r, c)
                rows = env.render().splitlines()
                self.assertEqual(len(rows), 20)
                self.assertTrue(all(len(row) == 20 for row in rows))
                for rr, row in enumerate(rows):
                    for cc, symbol in enumerate(row):
                        cell = (rr, cc)
                        if cell == (r, c):
                            expected = "*" if cell == goal else "A"
                        elif cell == goal:
                            expected = "G"
                        elif cell in obstacles:
                            expected = "#"
                        else:
                            expected = "."
                        self.assertEqual(symbol, expected)

    def test_human_matches_ansi(self):
        ansi = IcyGridWorldEnv(render_mode="ansi")
        human = IcyGridWorldEnv(render_mode="human")
        for position in ((19, 0), (4, 5), goal):
            ansi._position = human._position = position
            output = io.StringIO()
            with redirect_stdout(output):
                self.assertIsNone(human.render())
            self.assertEqual(output.getvalue(), ansi.render() + "\n")

    def test_human_renders_on_reset_and_step(self):
        env = IcyGridWorldEnv(render_mode="human")
        reference = IcyGridWorldEnv(render_mode="ansi")
        output = io.StringIO()
        with redirect_stdout(output):
            self.assertEqual(env.reset(seed=123), reference.reset(seed=123))
            first = reference.render()
            self.assertEqual(env.step(1), reference.step(1))
            second = reference.render()
        self.assertEqual(output.getvalue(), first + "\n" + second + "\n")

    def test_render_preserves_state_counter_and_rng(self):
        for mode in (None, "ansi", "human"):
            env = IcyGridWorldEnv(render_mode=mode)
            with redirect_stdout(io.StringIO()):
                env.reset(seed=123)
                env.step(1)
                state = (env._position, env._steps)
                rng = copy.deepcopy(env.np_random.bit_generator.state)
                env.render()
                env.render()
            self.assertEqual((env._position, env._steps), state)
            self.assertEqual(env.np_random.bit_generator.state, rng)

    def test_none_and_ansi_do_not_print(self):
        for mode in (None, "ansi"):
            env = IcyGridWorldEnv(render_mode=mode)
            output = io.StringIO()
            with redirect_stdout(output):
                env.reset(seed=0)
                env.step(1)
                result = env.render()
            self.assertEqual(output.getvalue(), "")
            if mode is None:
                self.assertIsNone(result)
            else:
                self.assertIsInstance(result, str)
