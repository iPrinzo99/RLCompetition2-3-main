"""Step contract, exhaustive branch checks, and seeded sampling checks."""

from collections import Counter
import copy
import random
import unittest
from unittest.mock import patch

import gymnasium as gym
import numpy as np

from icy_gridworld import decode, encode, goal, obstacles
from icy_gridworld.env import IcyGridWorldEnv


class ForcedChoice:
    def __init__(self, branch):
        self.branch = branch
        self.directions = None
        self.probabilities = None

    def choice(self, directions, p):
        self.directions = tuple(directions)
        self.probabilities = tuple(p)
        return directions[self.branch]


class StepTests(unittest.TestCase):
    def test_every_possible_branch_matches_kernel_and_contract(self):
        env = IcyGridWorldEnv()
        env.reset(seed=0)
        cells = {(r, c) for r in range(20) for c in range(20)} - obstacles
        direction_table = ((0, 3, 1), (1, 0, 2), (2, 1, 3), (3, 2, 0))
        checked = 0
        for r, c in cells - {goal}:
            neighbors = ((r - 1, c), (r, c + 1), (r + 1, c), (r, c - 1))
            for action in range(4):
                combined = Counter()
                for branch, probability in enumerate((0.8, 0.1, 0.1)):
                    env._position, env._steps = (r, c), 7
                    rng = ForcedChoice(branch)
                    env.np_random = rng
                    obs, reward, terminated, truncated, info = env.step(action)
                    executed = direction_table[action][branch]
                    attempted = neighbors[executed]
                    destination = attempted if attempted in cells else (r, c)
                    self.assertEqual(rng.directions, direction_table[action])
                    self.assertEqual(rng.probabilities, (0.8, 0.1, 0.1))
                    self.assertEqual(obs, encode(*destination))
                    self.assertIs(type(obs), int)
                    self.assertEqual(reward, 100.0 if destination == goal else -1.0)
                    self.assertIs(type(reward), float)
                    self.assertIs(terminated, destination == goal)
                    self.assertIs(truncated, False)
                    self.assertEqual(info, {"position": destination, "steps": 8,
                        "executed_action": executed, "slipped": executed != action,
                        "blocked": attempted not in cells})
                    self.assertIs(type(info["executed_action"]), int)
                    self.assertIs(type(info["slipped"]), bool)
                    self.assertIs(type(info["blocked"]), bool)
                    combined[obs] += probability
                    checked += 1
                expected = env.transition_probabilities(20 * r + c, action)
                self.assertEqual(dict(combined), expected)
        self.assertEqual(checked, 4212)

    def test_seeded_trajectories_and_reset_counter(self):
        first, second = IcyGridWorldEnv(), IcyGridWorldEnv()
        first.reset(seed=42)
        second.reset(seed=42)
        for action in [0, 1, 2, 3] * 300:
            result = first.step(action)
            self.assertEqual(result, second.step(action))
            if result[2]:
                self.assertEqual(first.reset(), second.reset())
        self.assertEqual(first.reset(), (380, {"position": (19, 0), "steps": 0}))

    def test_empirical_frequencies(self):
        env = IcyGridWorldEnv()
        env.reset(seed=2026)
        samples = 20000
        # Includes combined boundary outcomes, near-goal reward, and rock collision.
        for state, action in ((380, 2), (18, 1), (64, 1)):
            counts = Counter()
            for _ in range(samples):
                env._position = decode(state)
                counts[env.step(action)[0]] += 1
            expected = env.transition_probabilities(state, action)
            self.assertEqual(counts.keys(), expected.keys())
            for obs, probability in expected.items():
                # Six binomial standard deviations plus one sample of rounding.
                tolerance = 6 * (probability * (1 - probability) / samples) ** 0.5 + 1 / samples
                self.assertLessEqual(abs(counts[obs] / samples - probability), tolerance)

    def test_invalid_action_has_no_side_effects(self):
        env = IcyGridWorldEnv()
        env.reset(seed=123)
        before = copy.deepcopy(env.np_random.bit_generator.state)
        for action in (-1, 4, 1.0, "1", None, np.array([1])):
            with self.assertRaises(ValueError):
                env.step(action)
            self.assertEqual((env._position, env._steps), (env.start, 0))
            self.assertEqual(env.np_random.bit_generator.state, before)
        for action in (np.int64(1), np.array(1, dtype=np.int64)):
            env.step(action)

    def test_reset_required_and_goal_reward(self):
        env = IcyGridWorldEnv()
        with self.assertRaises(gym.error.ResetNeeded):
            env.step(1)
        env.reset(seed=0)
        env._position = (0, 18)
        env.np_random = ForcedChoice(0)
        result = env.step(1)
        self.assertEqual(result[:4], (19, 100.0, True, False))
        with self.assertRaises(gym.error.ResetNeeded):
            env.step(1)
        self.assertEqual(env.reset(seed=0)[0], 380)
        env.step(1)

    def test_base_does_not_truncate(self):
        env = IcyGridWorldEnv()
        env.reset(seed=0)
        env.np_random = ForcedChoice(0)
        for count in range(1, 502):
            result = env.step(2)
            self.assertEqual(result[:4], (380, -1.0, False, False))
            self.assertEqual(result[4]["steps"], count)

    def test_no_global_rng_used(self):
        env = IcyGridWorldEnv()
        env.reset(seed=0)
        python_state = random.getstate()
        numpy_state = copy.deepcopy(np.random.get_state())
        with patch("random.random", side_effect=AssertionError("global RNG")), \
             patch("numpy.random.choice", side_effect=AssertionError("global RNG")):
            for action in range(4):
                env.step(action)
        self.assertEqual(random.getstate(), python_state)
        current = np.random.get_state()
        self.assertEqual(current[0], numpy_state[0])
        np.testing.assert_array_equal(current[1], numpy_state[1])
        self.assertEqual(current[2:], numpy_state[2:])
