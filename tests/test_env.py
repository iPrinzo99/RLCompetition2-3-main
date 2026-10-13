"""Step 5 checks only: construction, reset, seeding, and exact queries."""

import copy
import unittest

import gymnasium as gym
import numpy as np

from icy_gridworld import encode, goal, obstacles, start, transition_probabilities
from icy_gridworld.env import IcyGridWorldEnv


class EnvironmentSetupTests(unittest.TestCase):
    def test_constructor_spaces_and_map(self):
        for mode in (None, "ansi", "human"):
            env = IcyGridWorldEnv(render_mode=mode)
            self.assertIsInstance(env, gym.Env)
            self.assertEqual(env.render_mode, mode)
            self.assertEqual(env.action_space, gym.spaces.Discrete(4))
            self.assertEqual(env.observation_space, gym.spaces.Discrete(400))
            self.assertEqual(env.metadata, {"render_modes": ["ansi", "human"], "render_fps": 4})
            self.assertIs(env.obstacles, obstacles)
            self.assertEqual(env.start, start)
            self.assertEqual(env.goal, goal)
            for cell in obstacles:
                self.assertTrue(env.observation_space.contains(encode(*cell)))
        with self.assertRaises(ValueError):
            IcyGridWorldEnv(render_mode="rgb_array")

    def test_reset_restores_fixed_state_and_fresh_info(self):
        env = IcyGridWorldEnv()
        obs, info = env.reset(seed=12)
        self.assertIs(type(obs), int)
        self.assertEqual((obs, info), (380, {"position": (19, 0), "steps": 0}))
        env._position = (0, 18)
        env._steps = 42
        info["steps"] = 999
        self.assertEqual(env.reset(options={"position": goal}),
                         (380, {"position": (19, 0), "steps": 0}))
        self.assertEqual((env._position, env._steps), (start, 0))

    def test_equal_seed_and_reseed(self):
        first, second = IcyGridWorldEnv(), IcyGridWorldEnv()
        first.reset(seed=123)
        second.reset(seed=123)
        expected = first.np_random.random(20)
        np.testing.assert_array_equal(expected, second.np_random.random(20))
        first.reset(seed=123)
        np.testing.assert_array_equal(expected, first.np_random.random(20))

    def test_seed_none_preserves_existing_stream(self):
        env = IcyGridWorldEnv()
        env.reset(seed=123)
        env.np_random.random(7)
        generator = env.np_random
        state = copy.deepcopy(generator.bit_generator.state)
        env.reset(seed=None)
        self.assertIs(env.np_random, generator)
        self.assertEqual(env.np_random.bit_generator.state, state)

    def test_query_method_all_pairs_without_state_or_rng_changes(self):
        env = IcyGridWorldEnv()
        env.reset(seed=123)
        before = copy.deepcopy(env.np_random.bit_generator.state)
        for state in range(400):
            if divmod(state, 20) not in obstacles:
                for action in range(4):
                    self.assertEqual(env.transition_probabilities(state, action),
                                     transition_probabilities(state, action))
        self.assertEqual(env.np_random.bit_generator.state, before)
        self.assertEqual((env._position, env._steps), (start, 0))

    def test_query_validation_and_numpy_actions(self):
        env = IcyGridWorldEnv()
        for action in (np.int64(1), np.array(1, dtype=np.int64)):
            self.assertTrue(env.action_space.contains(action))
            self.assertEqual(env.transition_probabilities(380, action),
                             transition_probabilities(380, 1))
        for action in (-1, 4, 1.0, "1", None, np.array([1])):
            for state in (380, 19):
                with self.assertRaises(ValueError):
                    env.transition_probabilities(state, action)
        for state in (-1, 400, 5):
            with self.assertRaises(ValueError):
                env.transition_probabilities(state, 0)
