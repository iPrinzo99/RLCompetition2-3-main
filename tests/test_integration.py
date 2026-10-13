"""Step 9 coverage of registered episodes and independent RNG consumers."""

from collections import Counter
import math
import unittest

import gymnasium as gym

import icy_gridworld
from icy_gridworld.env import IcyGridWorldEnv


class IntegrationTests(unittest.TestCase):
    def test_registered_episode_reproducibility_across_resets(self):
        with gym.make("IcyGridWorld-v0") as first, gym.make("IcyGridWorld-v0") as second:
            first.action_space.seed(456)
            second.action_space.seed(456)
            for episode in range(3):
                seed = 123 if episode == 0 else None
                self.assertEqual(first.reset(seed=seed), second.reset(seed=seed))
                for step in range(1, 501):
                    action = first.action_space.sample()
                    self.assertEqual(action, second.action_space.sample())
                    result = first.step(action)
                    self.assertEqual(result, second.step(action))
                    self.assertEqual(result[4]["steps"], step)
                    if result[2] or result[3]:
                        break
                self.assertTrue(result[2] or result[3])

    def test_queries_rendering_and_action_sampling_do_not_change_slips(self):
        with gym.make("IcyGridWorld-v0", render_mode="ansi") as first, \
             gym.make("IcyGridWorld-v0") as second:
            first.reset(seed=999)
            second.reset(seed=999)
            first.action_space.seed(321)
            observation = 380
            for action in [0, 1, 2, 3] * 100:
                first.render()
                for query_action in range(4):
                    first.unwrapped.transition_probabilities(observation, query_action)
                first.action_space.sample()
                result = first.step(action)
                self.assertEqual(result, second.step(action))
                observation = result[0]
                if result[2] or result[3]:
                    observation = first.reset()[0]
                    second.reset()

    def test_executed_direction_frequencies_for_every_action(self):
        env = IcyGridWorldEnv()
        env.reset(seed=9876)
        samples = 20000
        # Explicit expected distributions, independent of modulo computation.
        distributions = (
            {0: 0.8, 1: 0.1, 3: 0.1}, {1: 0.8, 0: 0.1, 2: 0.1},
            {2: 0.8, 1: 0.1, 3: 0.1}, {3: 0.8, 0: 0.1, 2: 0.1},
        )
        for action, expected in enumerate(distributions):
            counts = Counter()
            for _ in range(samples):
                env._position = (2, 2)
                result = env.step(action)
                counts[result[4]["executed_action"]] += 1
            self.assertEqual(counts.keys(), expected.keys())
            for direction, probability in expected.items():
                tolerance = 6 * math.sqrt(probability * (1 - probability) / samples) + 1 / samples
                self.assertLessEqual(abs(counts[direction] / samples - probability), tolerance)
