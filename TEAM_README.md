# Icy Grid World

Python package implementing the CIS 5930 Icy Grid World specification in `HW1.pdf`.
Requires Python 3.10 or later and Gymnasium 1.x.

## Status

Steps 1 through 10 are complete, including a runnable random-policy demonstration
and usage documentation. Forty-four tests pass with warnings treated as errors.
Final submission preparation (step 11) remains pending.

## Project structure

```text
icy_gridworld/__init__.py   Registration and public utility exports
icy_gridworld/map.py        Fixed obstacles, start, goal, encoding and decoding
icy_gridworld/movement.py   Executed directions and collision helper
icy_gridworld/transitions.py Exact transition probability function
icy_gridworld/env.py        Environment dynamics, exact queries, and text rendering
tests/README.md            Test scope and commands
tests/test_map.py          Map and encoding verification
tests/test_movement.py     Direction and collision verification
tests/test_transitions.py  Exact kernel verification
tests/test_env.py          Construction, reset, seeding, and method integration
tests/test_step.py         Step contract, exhaustive outcomes, and sampling
tests/test_render.py       Text layout, symbols, output, and state preservation
tests/test_registration.py Registration and termination/truncation boundaries
tests/test_integration.py  Registered episodes, RNG isolation, all-action sampling
tests/test_demo.py         Demo reproducibility, stopping conditions, CLI validation
demo.py                    Reproducible random-policy demonstration
pyproject.toml             Packaging, dependencies, and pytest configuration
requirements.txt           Editable installation with test dependencies
AI_LOG.md                  Record of AI-assisted work and verification
.gitignore                 Generated-file and local-secret exclusions
```

## Installation

From the project directory, using PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Gymnasium is constrained to `>=1.0,<2.0`. The test extra installs pytest 8.x.
These dependencies are declared in `pyproject.toml` so requirements do not need
to duplicate them.

## Tests

After installation:

```powershell
.\.venv\Scripts\python.exe -m pytest -q -W error
```

After installation, the tests can also run through unittest:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

These tests check the full obstacle layout, required counts, start and goal,
all 400 observation IDs, invalid inputs, and all 1,404 nonterminal cell/direction
combinations. Exact transition tests check all 1,408 traversable state/action
pairs, handout examples, merged outcomes, the absorbing goal, invalid inputs,
and repeatability. Environment setup tests verify spaces, map attributes, reset,
seed handling, and exact-query integration. Step tests cover all 4,212 nonterminal
state/action/slip combinations, 140,000 sampled transitions/directions, seeded trajectories,
invalid actions, terminal rewards, and absence of truncation in the base class.

## Fixed map and encoding

```python
from icy_gridworld import obstacles, start, goal, encode, decode

assert len(obstacles) == 48
assert encode(*start) == 380
assert encode(*goal) == 19
assert decode(380) == (19, 0)
```

Rows increase downward and columns increase rightward. The map has 352
traversable cells. `obstacles` is a frozenset of coordinate tuples; `start` and
`goal` are tuples. They are exposed both by the map module and as read-only-by-
convention attributes on the environment.

Encoding uses `20*r + c` and includes obstacle cells, as required by the declared
400-ID observation scheme. Helpers reject noninteger inputs (including booleans)
and out-of-bounds values. The transition helper additionally rejects obstacle IDs.

## Deterministic movement

`UP = 0`, `RIGHT = 1`, `DOWN = 2`, and `LEFT = 3`. Their displacement tuples are
`(-1, 0)`, `(0, 1)`, `(1, 0)`, and `(0, -1)`, respectively.

```python
from icy_gridworld import move, start, RIGHT, DOWN

assert move(start, RIGHT) == ((19, 1), False)
assert move(start, DOWN) == (start, True)
```

`move(position, direction)` returns `(next_position, blocked)` for an already
chosen executed direction. Hitting a rock or boundary returns the original
position and `True`. Entering the goal is allowed. The source must be traversable
and nonterminal; passing the goal as a source raises `ValueError`, consistent
with the nonterminal domain of the handout's collision rule. The exact transition
helper handles the absorbing goal before calling `move`.

This pure helper performs no random sampling and changes no environment state,
reward, or counter. Exact transition queries and sampled steps both use it.
The environment's `step` method handles the counter and reward.

## Exact transition probabilities

```python
from icy_gridworld import transition_probabilities

assert transition_probabilities(380, 2) == {380: 0.9, 381: 0.1}
assert transition_probabilities(19, 0) == {19: 1.0}
```

The function applies probability 0.80 to the intended direction and 0.10 to each
perpendicular direction, merging identical destinations after collisions. It
returns a fresh dictionary of encoded observations and positive probabilities
summing to one within floating-point tolerance. It neither samples randomness
nor mutates environment state. Invalid states and actions are rejected, including
invalid actions supplied with the goal state.

This function backs `IcyGridWorldEnv.transition_probabilities(self, state, action)`.
The environment method validates actions with `action_space.contains` and converts
accepted integer-like actions before delegating to the pure kernel.

## Environment setup and reset

```python
from icy_gridworld.env import IcyGridWorldEnv

env = IcyGridWorldEnv(render_mode=None)
assert env.reset(seed=123) == (380, {"position": (19, 0), "steps": 0})
assert env.transition_probabilities(19, 0) == {19: 1.0}
```

The class inherits `gymnasium.Env`, declares `Discrete(4)` actions and
`Discrete(400)` observations, and accepts None, `ansi`, or `human` as render modes.
Metadata declares both text modes and 4 FPS.
Reset first calls `super().reset(seed=seed)`, restores the fixed start and zero
steps, and ignores options. Reusing a seed reproduces RNG draws; `seed=None`
preserves the existing RNG stream. Exact queries leave state and RNG unchanged.
For normal episodes, use the registered environment shown below so the external
500-step time limit is applied. Direct class construction has no time limit.

Editable installation and all 44 tests were verified under Python 3.12.6 with
Gymnasium 1.3.0 and pytest 8.4.2. A standalone distribution build and execution
under Python 3.10 have not been verified.

## Sampled steps

```python
env = IcyGridWorldEnv()
observation, info = env.reset(seed=123)
observation, reward, terminated, truncated, info = env.step(1)
```

Each step validates the action, samples the executed direction with self.np_random
using probabilities (0.80, 0.10, 0.10), applies collisions, and increments the
counter. Entering the goal returns 100.0 and terminated=True; every other valid
transition returns -1.0, including collisions. Info contains position, steps,
executed_action, slipped, and blocked. Truncated is always False in this base
class, even after 500 steps; the registered TimeLimit wrapper enforces the limit.

Call reset before the first step and after termination. This implementation
raises Gymnasium ResetNeeded otherwise, an explicit guard outside the PDF's
required post-episode interface. Invalid actions cause no state or RNG changes.
Equal seeds and equal actions produce identical complete step results. The
learning algorithm, when present, should use the specified discount gamma=0.99;
step returns immediate rewards without applying discounting.

Gymnasium's full environment checker passes using the registered environment's
unwrapped instance, including automatic alternative-render-mode and close checks.
Dedicated wrapper tests verify the 500-step boundary and simultaneous flags.

## Registered environment and time limit

```python
import gymnasium as gym
import icy_gridworld  # Registers IcyGridWorld-v0 on import.

with gym.make("IcyGridWorld-v0", render_mode="ansi") as env:
    observation, info = env.reset(seed=123)
    observation, reward, terminated, truncated, info = env.step(1)
    print(env.render())
    probabilities = env.unwrapped.transition_probabilities(observation, 1)
```

Registration uses entry point `icy_gridworld.env:IcyGridWorldEnv` and
`max_episode_steps=500`. Gymnasium adds its TimeLimit wrapper automatically.
Before step 500, reaching the goal sets terminated=True and truncated=False.
Step 500 sets truncated=True; if that step also reaches the goal, both flags
are True. Reset after either flag becomes True; reset restarts the time limit
and environment counter. The wrapper does not change the transition kernel or
reward function. Package imports now require the declared Gymnasium dependency.

## Text rendering

```python
env = IcyGridWorldEnv(render_mode="ansi")
env.reset(seed=123)
print(env.render())
```

ANSI rendering returns 20 rows of 20 characters joined by newlines, without a
trailing newline. Symbols are A for the agent, G for uncollected gold, # for rocks,
and . for empty traversable cells. When the agent reaches the gold, * replaces
both A and G at that cell.

Human mode prints the same grid with a final newline and returns None. It also
prints automatically after reset and each successful step, following Gymnasium's
human-mode convention. With render_mode=None, render returns None and prints
nothing. Rendering preserves position, counter, and RNG state. No graphical
window or rgb_array mode is implemented.

## Demonstration

### Desktop viewer

```powershell
.\.venv\Scripts\python.exe gui.py
```

The desktop viewer uses Tkinter (included with standard Windows Python). Use the
arrow keys or buttons to move, Random play/Pause to sample actions at four steps
per second, and Reset episode to restart with the seed entered in the sidebar.
It displays the full map, reward, counter, requested/executed directions, slip and
collision indicators, and both episode flags. Controls stop when either flag is
true. This is a separate viewer; the specified environment render modes remain
None, ansi, and human. No new Python package dependency is required.

### Command-line demonstration

```powershell
.\.venv\Scripts\python.exe demo.py
```

This runs one random-policy episode through the registered environment, stopping
on termination or truncation, then prints steps, undiscounted total reward, final
observation/position, and both flags. The default seeds are 123 for ice slips and
456 for action selection. A random policy is not trained and may reach the time
limit without finding gold; that is a valid demonstration outcome.

Run two reproducible episodes and show each final grid:

```powershell
.\.venv\Scripts\python.exe demo.py --episodes 2 --seed 123 --action-seed 456 --render-mode ansi
```

Show the grid after every reset and step (potentially 501 grids per episode):

```powershell
.\.venv\Scripts\python.exe demo.py --render-mode human
```

Use `--help` to list options. Episodes must be positive; seeds must be nonnegative.
The first reset seeds ice slips; later episode resets use seed=None to continue
that stream. The action space is seeded separately once. Repeating the command
with the same dependency versions and seeds reproduces the run. The environment
is closed when the demonstration finishes.

The specified discount factor is gamma=0.99. A learning algorithm should compute
discounted return as the sum of gamma**t * reward[t] for t starting at zero. The
demo reports the ordinary sum of immediate rewards and does not train an agent.
Goal entry yields +100, replacing the normal -1 step reward. The absorbing goal
has zero subsequent mathematical reward, but Gymnasium callers reset after an
episode ends instead of stepping again.

With the verified dependency versions, the default run ended at step 500 with
total_reward=-500.0, observation=257, position=(12, 17), terminated=False, and
truncated=True. This is an example run, not a required trajectory across versions.

## Development record

See `AI_LOG.md` for the scope, changes, checks, and limitations of each completed step.
