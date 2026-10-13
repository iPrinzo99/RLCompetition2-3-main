"""Registration and the separation of MDP termination from external limits."""

from contextlib import redirect_stdout
import io
import subprocess
import sys
import unittest

import gymnasium as gym
from gymnasium.utils.env_checker import check_env
from gymnasium.wrappers import TimeLimit

import icy_gridworld
from icy_gridworld.env import IcyGridWorldEnv


class IntendedDirection:
    """Force intended movement for exact time-limit boundary tests."""

    def choice(self, directions, p):
        return directions[0]


class RegistrationTests(unittest.TestCase):
    def test_registered_spec_and_make(self):
        spec = gym.spec("IcyGridWorld-v0")
        self.assertEqual(spec.entry_point, "icy_gridworld.env:IcyGridWorldEnv")
        self.assertEqual(spec.max_episode_steps, 500)
        with gym.make("IcyGridWorld-v0") as env:
            self.assertIsInstance(env, TimeLimit)
            self.assertIsInstance(env.unwrapped, IcyGridWorldEnv)
            self.assertEqual(env.reset(seed=0), (380, {"position": (19, 0), "steps": 0}))
            self.assertEqual(env.unwrapped.transition_probabilities(19, 0), {19: 1.0})

    def test_fresh_process_import_registers(self):
        result = subprocess.run(
            [sys.executable, "-B", "-c",
             "import gymnasium as gym; import icy_gridworld; "
             "env=gym.make('IcyGridWorld-v0'); "
             "assert env.reset(seed=0)[0]==380; "
             "assert env.spec.max_episode_steps==500; env.close()"],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_truncates_exactly_at_500_and_reset_restarts_limit(self):
        with gym.make("IcyGridWorld-v0") as env:
            env.reset(seed=0)
            env.unwrapped.np_random = IntendedDirection()
            for count in range(1, 501):
                obs, reward, terminated, truncated, info = env.step(2)
                self.assertEqual((obs, reward, terminated), (380, -1.0, False))
                self.assertIs(truncated, count == 500)
                self.assertEqual(info["steps"], count)
            env.reset(seed=0)
            env.unwrapped.np_random = IntendedDirection()
            result = env.step(2)
            self.assertEqual(result[2:4], (False, False))
            self.assertEqual(result[4]["steps"], 1)

    def test_goal_before_limit_terminates_only(self):
        with gym.make("IcyGridWorld-v0") as env:
            env.reset(seed=0)
            env.unwrapped._position = (0, 18)
            env.unwrapped.np_random = IntendedDirection()
            self.assertEqual(env.step(1)[:4], (19, 100.0, True, False))

    def test_goal_on_transition_500_sets_both_flags(self):
        with gym.make("IcyGridWorld-v0") as env:
            env.reset(seed=0)
            env.unwrapped.np_random = IntendedDirection()
            for _ in range(499):
                self.assertEqual(env.step(2)[2:4], (False, False))
            # Set only position; both counters reached 499 through real steps.
            env.unwrapped._position = (0, 18)
            result = env.step(1)
            self.assertEqual(result[:4], (19, 100.0, True, True))
            self.assertEqual(result[4]["steps"], 500)

    def test_full_checker_with_registered_spec(self):
        with gym.make("IcyGridWorld-v0") as env:
            with redirect_stdout(io.StringIO()):
                check_env(env.unwrapped)
