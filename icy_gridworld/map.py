"""Fixed map and row-major observation encoding from HW1, section 2.1.

Map attributes are read-only by convention. Encoding covers every grid cell,
including obstacles; validation of traversable states belongs to the environment.
"""

from operator import index

GRID_SIZE = 20

obstacles = frozenset(
    {(r, 5) for r in range(16) if r not in {4, 12}}
    | {(r, 10) for r in range(4, 20) if r not in {8, 16}}
    | {(r, 15) for r in range(16) if r not in {6, 13}}
    | {(9, c) for c in range(6, 10) if c != 8}
    | {(14, c) for c in range(11, 15) if c != 13}
)
start = (19, 0)
goal = (0, 19)


def _bounded_integer(value: int, limit: int, name: str) -> int:
    """Accept integer-like values while rejecting booleans and invalid bounds."""
    if isinstance(value, bool):
        raise TypeError(f"{name} must be an integer, not a boolean")
    try:
        value = index(value)
    except TypeError as exc:
        raise TypeError(f"{name} must be an integer") from exc
    if not 0 <= value < limit:
        raise ValueError(f"{name} must be between 0 and {limit - 1}")
    return value


def encode(r: int, c: int) -> int:
    """Encode an in-bounds (row, column) as a Python integer, 20*r + c."""
    r = _bounded_integer(r, GRID_SIZE, "row")
    c = _bounded_integer(c, GRID_SIZE, "column")
    return GRID_SIZE * r + c


def decode(obs: int) -> tuple[int, int]:
    """Decode an observation ID in [0, 399] into (row, column)."""
    obs = _bounded_integer(obs, GRID_SIZE * GRID_SIZE, "observation")
    return divmod(obs, GRID_SIZE)
