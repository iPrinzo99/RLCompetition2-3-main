"""Deterministic executed-direction movement (HW1 sections 2.2 and 2.3)."""

from .map import GRID_SIZE, _bounded_integer, decode, encode, goal, obstacles

UP, RIGHT, DOWN, LEFT = 0, 1, 2, 3
DISPLACEMENTS = ((-1, 0), (0, 1), (1, 0), (0, -1))


def move(position: tuple[int, int], direction: int) -> tuple[tuple[int, int], bool]:
    """Return (next_position, blocked) for an executed direction.

    The source must be a traversable, nonterminal cell, as in the handout's
    definition of m(s, b). The future transition kernel must handle the absorbing
    goal separately. This helper does not sample slips or track steps/rewards.
    """
    direction = _bounded_integer(direction, len(DISPLACEMENTS), "direction")
    r, c = decode(encode(*position))
    position = (r, c)
    if position in obstacles:
        raise ValueError("source position must not be an obstacle")
    if position == goal:
        raise ValueError("movement requires a nonterminal source position")

    dr, dc = DISPLACEMENTS[direction]
    destination = (r + dr, c + dc)
    blocked = not (
        0 <= destination[0] < GRID_SIZE and 0 <= destination[1] < GRID_SIZE
    ) or destination in obstacles
    return (position if blocked else destination), blocked
