"""Exact transition kernel from HW1 sections 2.4 and 3.4, without sampling."""

from .map import _bounded_integer, decode, encode, goal, obstacles
from .movement import move


def transition_probabilities(state: int, action: int) -> dict[int, float]:
    """Return {next_observation: probability}, with duplicate outcomes merged.

    This pure function supplies the kernel for the environment query method.
    State IDs must identify traversable cells; actions must be integers 0..3.
    """
    position = decode(state)
    action = _bounded_integer(action, 4, "action")
    if position in obstacles:
        raise ValueError("state must identify a traversable cell, not an obstacle")
    if position == goal:
        return {encode(*goal): 1.0}

    probabilities: dict[int, float] = {}
    for direction, probability in (
        (action, 0.80), ((action - 1) % 4, 0.10), ((action + 1) % 4, 0.10)
    ):
        destination, _ = move(position, direction)
        observation = encode(*destination)
        probabilities[observation] = probabilities.get(observation, 0.0) + probability
    return probabilities
