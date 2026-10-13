"""Icy Grid World utilities and Gymnasium environment registration."""

from gymnasium.envs.registration import register

from .map import GRID_SIZE, decode, encode, goal, obstacles, start
from .movement import DISPLACEMENTS, DOWN, LEFT, RIGHT, UP, move
from .transitions import transition_probabilities

register(
    id="IcyGridWorld-v0",
    entry_point="icy_gridworld.env:IcyGridWorldEnv",
    max_episode_steps=500,
)

__all__ = [
    "GRID_SIZE", "decode", "encode", "goal", "obstacles", "start",
    "DISPLACEMENTS", "DOWN", "LEFT", "RIGHT", "UP", "move",
    "transition_probabilities",
]
