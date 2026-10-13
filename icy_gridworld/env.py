"""Icy Grid World dynamics, exact queries, and text rendering."""

import gymnasium as gym

from .map import GRID_SIZE, encode, goal, obstacles, start
from .movement import move
from .transitions import transition_probabilities


class IcyGridWorldEnv(gym.Env):
    """Fixed Icy Grid World map with a reproducibly seeded reset."""

    metadata = {"render_modes": ["ansi", "human"], "render_fps": 4}
    obstacles = obstacles
    start = start
    goal = goal

    def __init__(self, render_mode=None):
        if render_mode not in (None, "ansi", "human"):
            raise ValueError("render_mode must be None, 'ansi', or 'human'")
        self.render_mode = render_mode
        self.action_space = gym.spaces.Discrete(4)
        self.observation_space = gym.spaces.Discrete(400)
        self._position = self.start
        self._steps = 0
        self._has_reset = False

    def reset(self, *, seed=None, options=None):
        super().reset(seed=seed)
        self._position = self.start
        self._steps = 0
        self._has_reset = True
        if self.render_mode == "human":
            self.render()
        return encode(*self._position), {"position": self._position, "steps": self._steps}

    def step(self, action):
        if not self.action_space.contains(action):
            raise ValueError("action must belong to Discrete(4)")
        if not self._has_reset or self._position == self.goal:
            raise gym.error.ResetNeeded("Call reset() before starting a new episode")
        action = int(action)
        executed_action = int(self.np_random.choice(
            (action, (action - 1) % 4, (action + 1) % 4), p=(0.80, 0.10, 0.10)
        ))
        self._position, blocked = move(self._position, executed_action)
        self._steps += 1
        terminated = self._position == self.goal
        reward = 100.0 if terminated else -1.0
        if self.render_mode == "human":
            self.render()
        return encode(*self._position), reward, terminated, False, {
            "position": self._position,
            "steps": self._steps,
            "executed_action": executed_action,
            "slipped": executed_action != action,
            "blocked": blocked,
        }

    def render(self):
        """Return the ANSI grid or print the same grid in human mode."""
        if self.render_mode is None:
            return None
        rows = [["."] * GRID_SIZE for _ in range(GRID_SIZE)]
        for r, c in self.obstacles:
            rows[r][c] = "#"
        rows[self.goal[0]][self.goal[1]] = "G"
        r, c = self._position
        rows[r][c] = "*" if self._position == self.goal else "A"
        text = "\n".join("".join(row) for row in rows)
        if self.render_mode == "ansi":
            return text
        print(text)
        return None

    def transition_probabilities(self, state, action):
        """Return {next_observation: probability}, with duplicate outcomes merged."""
        if not self.action_space.contains(action):
            raise ValueError("action must belong to Discrete(4)")
        return transition_probabilities(state, int(action))
