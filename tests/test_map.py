"""Verify the map against the handout diagram and all 400 observation IDs."""

import unittest

from icy_gridworld import GRID_SIZE, decode, encode, goal, obstacles, start


class MapTests(unittest.TestCase):
    def test_map_matches_handout(self):
        rows = (
            ".....#.........#...G",
            ".....#.........#....",
            ".....#.........#....",
            ".....#.........#....",
            "..........#....#....",
            ".....#....#....#....",
            ".....#....#.........",
            ".....#....#....#....",
            ".....#.........#....",
            ".....###.##....#....",
            ".....#....#....#....",
            ".....#....#....#....",
            "..........#....#....",
            ".....#....#.........",
            ".....#....###.##....",
            ".....#....#....#....",
            "....................",
            "..........#.........",
            "..........#.........",
            "S.........#.........",
        )
        self.assertEqual(GRID_SIZE, 20)
        self.assertEqual(len(rows), 20)
        self.assertTrue(all(len(row) == 20 for row in rows))
        expected = {(r, c) for r, row in enumerate(rows)
                    for c, char in enumerate(row) if char == "#"}
        self.assertIsInstance(obstacles, frozenset)
        self.assertEqual(obstacles, expected)
        self.assertEqual(len(obstacles), 48)
        self.assertEqual(400 - len(obstacles), 352)

    def test_start_and_goal(self):
        self.assertEqual(start, (19, 0))
        self.assertEqual(goal, (0, 19))
        self.assertIsInstance(start, tuple)
        self.assertIsInstance(goal, tuple)
        self.assertNotIn(start, obstacles)
        self.assertNotIn(goal, obstacles)
        self.assertEqual(encode(*start), 380)
        self.assertEqual(encode(*goal), 19)

    def test_all_observation_ids(self):
        for obs in range(400):
            with self.subTest(obs=obs):
                r, c = decode(obs)
                self.assertEqual((r, c), (obs // 20, obs % 20))
                self.assertEqual(encode(r, c), obs)
                self.assertIs(type(encode(r, c)), int)
        self.assertEqual(encode(0, 5), 5)  # Obstacle IDs are encodable.
        self.assertEqual(decode(5), (0, 5))

    def test_invalid_inputs(self):
        for value in (-1, 20):
            with self.assertRaises(ValueError):
                encode(value, 0)
            with self.assertRaises(ValueError):
                encode(0, value)
        for value in (-1, 400):
            with self.assertRaises(ValueError):
                decode(value)
        for value in (1.5, "1", None, True):
            with self.assertRaises(TypeError):
                encode(value, 0)
            with self.assertRaises(TypeError):
                encode(0, value)
            with self.assertRaises(TypeError):
                decode(value)
