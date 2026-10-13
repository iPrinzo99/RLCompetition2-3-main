"""Independent checks of the exact kernel, including every state/action pair."""

from fractions import Fraction
import random
import unittest

from icy_gridworld import decode, encode, goal, obstacles, transition_probabilities


class TransitionTests(unittest.TestCase):
    def assert_distribution(self, actual, expected):
        self.assertEqual(actual.keys(), expected.keys())
        for state, probability in expected.items():
            self.assertAlmostEqual(actual[state], float(probability), places=14)

    def test_handout_examples(self):
        self.assert_distribution(transition_probabilities(380, 1),
                                 {381: 0.8, 360: 0.1, 380: 0.1})
        self.assert_distribution(transition_probabilities(380, 2),
                                 {380: 0.9, 381: 0.1})
        self.assert_distribution(transition_probabilities(18, 1),
                                 {19: 0.8, 18: 0.1, 38: 0.1})

    def test_absorbing_goal(self):
        for action in range(4):
            self.assertEqual(transition_probabilities(19, action), {19: 1.0})

    def test_all_state_action_pairs(self):
        cells = {(r, c) for r in range(20) for c in range(20)} - obstacles
        # Explicit direction/weight table, independent of modulo slip logic.
        weights = ((8, 1, 0, 1), (1, 8, 1, 0), (0, 1, 8, 1), (1, 0, 1, 8))
        checked = 0
        for r, c in cells:
            neighbors = ((r - 1, c), (r, c + 1), (r + 1, c), (r, c - 1))
            for action in range(4):
                with self.subTest(position=(r, c), action=action):
                    expected = {}
                    if (r, c) == goal:
                        expected = {19: Fraction(1)}
                    else:
                        for candidate, weight in zip(neighbors, weights[action]):
                            if weight:
                                nr, nc = candidate if candidate in cells else (r, c)
                                obs = 20 * nr + nc
                                expected[obs] = expected.get(obs, Fraction(0)) + Fraction(weight, 10)
                    result = transition_probabilities(20 * r + c, action)
                    self.assert_distribution(result, expected)
                    self.assertAlmostEqual(sum(result.values()), 1.0, places=14)
                    for obs, probability in result.items():
                        self.assertIs(type(obs), int)
                        self.assertIs(type(probability), float)
                        self.assertGreater(probability, 0)
                        self.assertIn(decode(obs), cells)
                    checked += 1
        self.assertEqual(checked, 1408)

    def test_invalid_inputs(self):
        for cell in obstacles:
            with self.assertRaises(ValueError):
                transition_probabilities(encode(*cell), 0)
        for state in (-1, 400):
            with self.assertRaises(ValueError):
                transition_probabilities(state, 0)
        for state in (380, 19):
            for action in (-1, 4):
                with self.assertRaises(ValueError):
                    transition_probabilities(state, action)
            for action in (1.5, "1", None, True):
                with self.assertRaises(TypeError):
                    transition_probabilities(state, action)
        for state in (1.5, "380", None, True):
            with self.assertRaises(TypeError):
                transition_probabilities(state, 0)

    def test_repeatability_and_independent_results(self):
        rng_before = random.getstate()
        first = transition_probabilities(380, 2)
        second = transition_probabilities(380, 2)
        self.assertEqual(first, second)
        self.assertIsNot(first, second)
        first.clear()
        self.assertEqual(transition_probabilities(380, 2), second)
        self.assertEqual(random.getstate(), rng_before)
