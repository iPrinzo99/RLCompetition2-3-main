"""Tests for the deterministic collision rule, before stochastic transitions."""

import unittest

from icy_gridworld import (
    DISPLACEMENTS, DOWN, LEFT, RIGHT, UP, goal, move, obstacles, start,
)


class MovementTests(unittest.TestCase):
    def test_action_conventions(self):
        self.assertEqual((UP, RIGHT, DOWN, LEFT), (0, 1, 2, 3))
        self.assertEqual(DISPLACEMENTS, ((-1, 0), (0, 1), (1, 0), (0, -1)))
        self.assertEqual([move((2, 2), a) for a in range(4)], [
            ((1, 2), False), ((2, 3), False),
            ((3, 2), False), ((2, 1), False),
        ])

    def test_start_boundary_examples(self):
        self.assertEqual(move(start, RIGHT), ((19, 1), False))
        self.assertEqual(move(start, UP), ((18, 0), False))
        self.assertEqual(move(start, DOWN), (start, True))
        self.assertEqual(move(start, LEFT), (start, True))

    def test_rocks_gaps_and_goal_entry(self):
        self.assertEqual(move((3, 4), RIGHT), ((3, 4), True))
        self.assertEqual(move((4, 4), RIGHT), ((4, 5), False))
        self.assertEqual(move((8, 7), DOWN), ((8, 7), True))
        self.assertEqual(move((8, 8), DOWN), ((9, 8), False))
        self.assertEqual(move((0, 18), RIGHT), (goal, False))
        self.assertEqual(move((1, 19), UP), (goal, False))

    def test_every_nonterminal_cell_and_direction(self):
        # Build legal neighbor edges independently, without using DISPLACEMENTS.
        cells = {(r, c) for r in range(20) for c in range(20)} - obstacles
        checked = 0
        for r, c in cells - {goal}:
            candidates = ((r - 1, c), (r, c + 1), (r + 1, c), (r, c - 1))
            for direction, neighbor in enumerate(candidates):
                with self.subTest(position=(r, c), direction=direction):
                    destination, blocked = move((r, c), direction)
                    self.assertEqual(destination, neighbor if neighbor in cells else (r, c))
                    self.assertIs(blocked, neighbor not in cells)
                    self.assertIn(destination, cells)
                    self.assertIsInstance(destination, tuple)
                    checked += 1
        self.assertEqual(checked, 1404)

    def test_invalid_sources_and_directions(self):
        for position in ((0, 5), (-1, 0), (20, 0), (0, 20), goal):
            with self.subTest(position=position), self.assertRaises(ValueError):
                move(position, UP)
        for direction in (-1, 4):
            with self.assertRaises(ValueError):
                move(start, direction)
        for direction in (1.5, "1", None, True):
            with self.assertRaises(TypeError):
                move(start, direction)
