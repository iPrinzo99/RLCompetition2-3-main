# AI assistance log

## 2026-09-15 - Step 1: project setup

### Authorization and scope

The user requested implementation of step 1 only, documentation of everything
done, and a stop before any later step without explicit instruction. Codex created
the scaffold below. No environment behavior was implemented.

### Initial inspection

- Inspected the workspace, including hidden entries and Git status. It contained
  an existing `.git` directory and `tmp/` with earlier PDF-review output, but no
  project source files.
- Checked for `AGENTS.md` in the workspace and ancestor directories; none was found.
- Confirmed the available `python` reports Python 3.12.6, satisfying Python 3.10+.
- Preserved the existing Git directory and PDF-review scratch files.

### Files created

- `icy_gridworld/__init__.py`: importable package with a scaffold docstring only.
- `tests/README.md`: preserves the test directory and records that tests are pending.
- `demo.py`: a main entry point that prints an explicit scaffold-only message.
- `pyproject.toml`: setuptools build backend, package name `icy_gridworld`, initial
  version `0.1.0`, Python `>=3.10`, Gymnasium `>=1.0,<2.0`, a pytest `>=8,<9` test
  extra, package discovery limited to `icy_gridworld*`, and pytest test-directory
  configuration.
- `requirements.txt`: installs the local package in editable mode with its test
  extra using `-e .[test]`; dependency declarations remain in `pyproject.toml`.
- `.gitignore`: excludes virtual environments, Python caches, build output, test
  and coverage output, common local secret files, and `tmp/` scratch files.
- `README.md`: documents scaffold status, file structure, Python requirements,
  PowerShell virtual-environment and installation commands, future test command,
  placeholder demo command, and the absence of implemented environment behavior.
- `AI_LOG.md`: this record, written after the scaffold checks completed.

### Verification performed and results

- Parsed `pyproject.toml` with Python's `tomllib`: passed.
- Checked Python and Gymnasium version constraints: passed.
- Checked existence of all scaffold files created before this log: passed.
- Parsed both Python source files using `ast.parse`: passed.
- Imported `icy_gridworld` using Python with bytecode writes disabled: passed.
- Ran `python -B demo.py`: passed; printed
  `Project scaffold only. The environment demonstration is not implemented yet.`
- Inspected Git status: the new scaffold files were untracked as expected.
- Used `git check-ignore` to verify scratch PDF renders, `.venv/`, `.env`, and
  Python cache paths are ignored: passed.

### Limits and stopping point

No virtual environment was created and no dependencies were installed. Installation
and wheel building have not been tested. No behavioral tests were created or run;
the README explicitly notes that pytest currently collects no tests. No Git commit,
remote repository, upload, or course submission was made. The existing repository
was not reinitialized.

Step 1 is complete. Map constants, movement, transition probabilities, the Env
class, registration, rendering, and a real demo remain for later steps. Stop here
and wait for explicit user instruction before continuing.

## 2026-09-15 - Step 2: fixed map and observation encoding

### Authorization and inspection

The user authorized step 2 only, requested documentation after completion, and
required a stop before step 3. The preceding interrupted attempt issued only a
commentary message; it made no tool calls or file changes. Read the existing
package, configuration, README, and step 1 log, searched for workspace AGENTS.md
files (none found), and inspected Git status before editing.

### Implementation completed

- Created `icy_gridworld/map.py` with `GRID_SIZE = 20` and all five obstacle
  sets translated directly from the specification's equations. Their union is
  stored as a frozenset of coordinate tuples named `obstacles`.
- Defined `start = (19, 0)` and `goal = (0, 19)` as tuples. These module attributes
  are read-only by convention. Exposing them on the future environment instance
  remains part of implementing the class in step 5.
- Implemented `encode(r, c)` as `20*r + c` and `decode(obs)` using `divmod(obs, 20)`.
  Both cover the entire grid, including obstacle IDs. No movement or state
  transition logic was added.
- Added integer and bounds validation. Integer-like inputs accepted by
  `operator.index` are supported; booleans and nonintegers raise TypeError, and
  out-of-range inputs raise ValueError. This is a utility design choice; obstacle
  rejection for transition queries remains a later requirement.
- Updated `icy_gridworld/__init__.py` to export the map attributes and helpers.
- Created `tests/test_map.py` with four unittest tests, compatible with pytest.
  The independent diagram fixture checks the obstacle equations against the
  handout's complete 20-row illustration rather than repeating those equations.

### Verification results

Ran `python -B -m unittest discover -s tests -v`: all four tests passed.
Checks verified the full obstacle layout, 48 obstacles, 352 traversable cells,
tuple start/goal outside obstacles, start observation 380, goal observation 19,
round trips for all 400 observation IDs, Python integer encoding results,
encoding of obstacle cells, and invalid input handling.

Ran `git diff --check`: no diagnostics. Because the scaffold remains untracked,
this Git check does not validate the contents of those untracked files; the
executed tests provide the functional verification for this step.

### Documentation and stopping point

After implementation and verification, updated README.md with step 2 status,
file structure, map semantics, helper examples, and the dependency-free test
command. Updated tests/README.md with test scope and invocation. Appended this
record to AI_LOG.md, preserving the historical step 1 entry.

No dependencies were installed, no virtual environment was created, and no Git
commit or upload was made. Installation and packaging remain unverified. The
placeholder demo is unchanged. Step 2 is complete; movement logic (step 3) and
all subsequent implementation await explicit user instruction.

## 2026-09-15 - Step 3: shared deterministic movement

### Authorization and inspection

The user authorized only step 3, requested documentation after completion, and
required a stop before any later step. Read the existing map, package exports,
README, test documentation, and the end of this log. Searched for workspace
AGENTS.md files (none found) and inspected Git status. Existing files remain
untracked. Used the specification's sections 2.2 and 2.3, already read in this
conversation, as the movement contract.

### Implementation completed

- Created `icy_gridworld/movement.py` with action constants UP=0, RIGHT=1, DOWN=2,
  LEFT=3 and immutable displacement tuples (-1,0), (0,1), (1,0), (0,-1).
- Added `move(position, direction)` returning `(next_position, blocked)`. It
  applies the executed direction directly. An obstacle or boundary collision
  returns the source position and Python boolean True; a legal move returns the
  destination and False. Entering the goal is allowed.
- Reused existing integer/bounds and coordinate helpers. Invalid direction types
  or bounds are rejected. Obstacle sources and the terminal goal source raise
  ValueError. The latter is a deliberate precondition matching the handout's
  definition of movement for nonterminal states; the later transition kernel must
  handle absorbing-goal queries before invoking this helper.
- Kept movement deterministic and free of mutable environment state, RNG use,
  reward calculation, and counters. This prepares the shared helper for steps 4
  and 6 without implementing those steps.
- Updated package exports to include the action constants, displacements, and move.
- Created `tests/test_movement.py` with five tests covering action conventions,
  the handout's start-cell directional outcomes, rock collisions and open gaps,
  entry into the goal from both neighbors, invalid inputs, and an exhaustive
  comparison against legal neighbor cells for all 351 nonterminal states and
  four directions (1,404 combinations).

### Verification results

- `python -B -m unittest discover -s tests -v`: all nine tests passed, including
  the four existing map/encoding tests and five new movement tests.
- Parsed all five package/test Python files with `ast.parse` using Python 3.10
  grammar: passed. This is a syntax check, not execution under Python 3.10.

### Documentation and stopping point

After the implementation and checks passed, updated README.md with step 3 status,
new file entries, test coverage, movement examples, and the helper's nonterminal
source precondition. Updated tests/README.md with the five new tests and total
passing count. Appended this complete step 3 record to AI_LOG.md.

No dependencies were installed, no existing map constants were changed, and no
Git commit or upload was made. The placeholder demo remains unchanged. Packaging
and installation remain unverified. Step 3 is complete. Step 4 (exact transition
probabilities) and all subsequent steps await explicit user instruction.

## 2026-09-15 - Step 4: exact transition kernel

### Authorization and inspection

After clarification, the user explicitly authorized step 4 only, requested a
complete record afterward, and required a stop before step 5. Read the current
map, movement module, package exports, README, and log tail. Searched for workspace
AGENTS.md files; none was found (rg exit code 1 means no matches).

### Implementation completed

- Created `icy_gridworld/transitions.py` with a pure function named
  `transition_probabilities(state, action)`, using integer observation IDs.
- Reused coordinate/input validation and the shared `move` collision helper.
- Applied 0.80 to the requested direction and 0.10 to each perpendicular direction,
  with no backward slip, and merged probabilities for repeated destinations.
- Handled the goal before invoking movement, returning a fresh `{19: 1.0}`.
- Rejected all obstacle IDs, out-of-range IDs, invalid actions, and unsupported
  types. Action validation runs before the absorbing-goal return.
- Used no random sampling, mutable environment state, rewards, or step counters.
- Exported the function from the package. The required environment instance method
  remains an integration item for step 5, because that step creates the Env class.
  This is a staging decision, not a change to the final specification's API.
- Added five tests in `tests/test_transitions.py`. The exhaustive oracle uses an
  explicit direction-weight table and Fraction arithmetic rather than the
  implementation's modulo-based slip selection or movement helper.

### Verification results

Ran `python -B -m unittest discover -s tests -v`: all 14 tests passed, comprising
nine regression tests and five transition tests. Verified all 352 traversable
states times four actions (1,408 pairs), correct destination IDs, positive Python
float probabilities, sums within 1e-14 tolerance, and agreement with the oracle.
Verified the handout's start-RIGHT, start-DOWN, and near-goal-RIGHT examples,
including merged self-loop probabilities. Checked absorbing-goal behavior for
all actions, all 48 invalid obstacle IDs, invalid bounds/types, repeated identical
queries, independent returned dictionaries, and unchanged Python random state.
Source inspection confirms no sampling in the kernel or its helper call chain.

Parsed all seven package/test Python files with Python 3.10 grammar: passed.
This verifies syntax, not execution under a Python 3.10 interpreter.

### Documentation and stopping point

After implementation and successful checks, updated README.md with step 4 status,
file entries, test coverage, examples, and the explicit pending instance-method
integration. Updated tests/README.md with the new tests and appended this log.

No dependencies were installed, no environment class or sampled step was added,
and no Git commit or upload was made. The placeholder demo is unchanged.
Installation/build verification remains pending. Step 4's standalone kernel is
complete; step 5 and all subsequent work await explicit user instruction.

## 2026-09-15 - Step 5: constructor, reset, and query-method integration

### Authorization and inspection

The user authorized step 5 only, documentation afterward, and a stop before step 6.
Read the current transition kernel, packaging configuration, README status, and
log tail. Searched for workspace AGENTS.md files (none found). Checked installed
modules: system Python had NumPy, but neither Gymnasium nor pytest.

### Implementation completed

- Added `icy_gridworld/env.py` containing `IcyGridWorldEnv(gymnasium.Env)` with
  the exact constructor signature `__init__(self, render_mode=None)`.
- Validated render modes None, ansi, human; set the required render metadata,
  Discrete(4) action space, and Discrete(400) observation space.
- Exposed obstacles, start, and goal as read-only-by-convention class attributes
  referencing the existing fixed map. Initialized position and step counter.
- Added `reset(self, *, seed=None, options=None)` whose first operational line is
  `super().reset(seed=seed)`. Reset restores the start and counter, ignores options,
  and returns `(380, {"position": (19, 0), "steps": 0})` with fresh info.
- Added the required instance transition_probabilities method, completing step 4's
  integration item. It validates actions through action_space.contains, normalizes
  accepted actions to Python integers, and delegates to the exact kernel. This
  supports NumPy integer scalars and accepted zero-dimensional integer arrays.
- Left step, render, registration, rewards, and episode termination unimplemented.
  The class is imported directly from icy_gridworld.env; package-level utility
  imports remain independent of Gymnasium.
- Added six environment setup tests in tests/test_env.py.

### Dependency setup and verification

The initial `python -m venv .venv` failed bootstrapping ensurepip; the subsequent
pip command reported no pip module. Requested an escalated retry to finish setup
and install declared dependencies. The retry succeeded: created the ignored .venv
and installed requirements.txt, including the editable package, Gymnasium 1.3.0,
pytest 8.4.2, NumPy 2.5.3, and their dependencies. No global Python packages were
changed. Editable wheel creation/installation succeeded; a standalone wheel or
source distribution build was not tested.

Ran `.venv/Scripts/python.exe -B -m pytest -q -p no:cacheprovider`: all 20 tests
passed under Python 3.12.6. New checks cover all allowed constructor modes, spaces
and map attributes, obstacle membership in the observation-space superset, reset
after altered state/counter, fresh info, ignored options, equal seeds/reseeding,
and unchanged existing RNG stream on reset(seed=None). Compared the instance
query method with the kernel across all 1,408 valid pairs without changing state
or RNG. Tested NumPy actions and invalid action/state rejection.

Ran pip check: no broken requirements. Parsed env.py using Python 3.10 grammar
and inspected its reset AST: confirmed the first statement is the required super
call. Full trajectory reproducibility and Gymnasium's full environment checker
remain pending because sampled step and rendering are not yet implemented.

### Documentation and stopping point

After implementation and successful checks, updated README.md with step 5 status,
new files, environment usage, installed test commands, method integration, and
verification limits. Updated tests/README.md and the kernel docstring's outdated
future-method wording. Appended this record. No Git commits or uploads were made;
the placeholder demo is unchanged. Step 5 is complete; stop before step 6 and wait
for explicit user instruction.

## Step 6: sampled steps, rewards, termination, and info

### Authorization and inspection

The user authorized step 6 only, documentation after completion, and a stop before
step 7, and repeated that instruction during implementation. Read env.py, the
transition kernel, README tail, and log tail. Searched for workspace AGENTS.md
outside Git and the virtual environment; none found.

### Implementation completed

- Added IcyGridWorldEnv.step(action). Validated actions using action_space.contains
  and normalized accepted actions to Python integers.
- Sampled the requested direction or its two perpendicular directions using only
  self.np_random.choice with probabilities (0.80, 0.10, 0.10).
- Reused move for collisions, updated position, and incremented the step counter
  for every valid transition, including blocked moves.
- Returned Python integer observations, Python float rewards (100.0 on goal entry,
  -1.0 otherwise), terminated exactly on goal entry, and truncated=False.
- Returned all required info fields: tuple position, steps, integer executed_action,
  boolean slipped, and boolean blocked.
- Added _has_reset initialization/reset tracking and a ResetNeeded guard before
  the first reset or after reaching the goal. This is a deliberate defensive
  behavior outside the required post-terminal calling contract. The exact goal
  kernel remains absorbing. Invalid actions are rejected before RNG/state changes.
- Updated the environment module docstring. Did not add rendering, registration,
  TimeLimit wrapping, or demo behavior.

### Tests and results

Added tests/test_step.py with seven tests. Forced-choice RNG injection exercises
all 351 nonterminal positions times four actions times three slip branches
(4,212 cases). It independently checks direction selection, supplied weights,
destinations, reward, flags, counter, info values/types, and aggregates outcomes
to compare directly with the exact query kernel. Forced injection is confined to
tests; production uses the Gymnasium generator.

Additional tests verify equal-seed full result sequences for 1,200 action requests,
reset counters, 60,000 real sampled transitions across three representative
distributions (merged boundary, goal entry, obstacle collision), invalid-action
state/RNG preservation, NumPy actions, reset guards, +100 rather than +99 at the
goal, 501 blocked steps without base truncation, and unchanged global Python/NumPy
RNG states. Frequency tolerances use six binomial standard deviations plus one
sample of rounding, with a fixed seed for repeatability.

Ran `.venv/Scripts/python.exe -B -m pytest -q -p no:cacheprovider`: all 27 tests
passed. Ran Gymnasium check_env(IcyGridWorldEnv(), skip_render_check=True): passed.
Rendering checks were explicitly skipped because step 7 is not authorized yet.
No dependencies were added or changed.

### Documentation and stopping point

After implementation and verification, updated README.md with step 6 status,
new test file/coverage, sampled-step usage, rewards/flags/info, reset guards,
gamma guidance, and pending wrapper/rendering limitations. Updated tests/README.md
with verification details and appended this record. Earlier step entries are
historical records. No Git commit or upload was made. Step 6 is complete; stop
before step 7 and await explicit user instruction.

## Step 7: ANSI and human text rendering

### Authorization and inspection

The user authorized step 7 only, documentation afterward, and a stop before step 8.
Read env.py, README and log tails, and searched for workspace AGENTS.md files
outside Git and .venv; none was found. Used the already-read PDF section 3.7
for dimensions, symbols, metadata, and supported modes.

### Implementation completed

- Implemented render() in env.py using GRID_SIZE and the existing fixed map.
- ANSI mode returns 20 rows of exactly 20 characters joined by newline characters,
  with no trailing newline. Uses A, G, #, and .; goal occupancy is rendered as *.
- Human mode prints the identical representation with a final newline and returns
  None. Added automatic human-mode rendering after reset and each valid step,
  consistent with Gymnasium human-mode behavior. ANSI/None remain silent.
- With render_mode=None, render() returns None. Rendering does not sample RNG or
  modify position, step count, or episode state. No window, graphical dependency,
  or rgb_array mode was added. Existing metadata already matched the PDF.
- Updated the environment module description and imported GRID_SIZE for layout.
- Added five tests in tests/test_render.py covering every displayed cell for each
  of 352 traversable positions (140,800 symbol comparisons), dimensions, human/ANSI
  equality at start, a map gap, and goal, automatic human output, silent modes,
  and state/counter/RNG preservation.

### Verification results

Ran `.venv/Scripts/python.exe -B -m pytest -q -p no:cacheprovider`: all 32 tests
passed, including all prior map, movement, transition, reset, and step checks.
Ran Gymnasium check_env separately for None, ansi, and human modes with rendering
checks enabled, capturing printed grids to avoid noisy output. All three passed.
The checker issued the expected warning that it cannot automatically instantiate
alternative render modes without a registered spec. Separate explicit mode checks
were performed; registration and wrapper checks remain for step 8.

### Documentation and stopping point

After successful implementation and verification, updated README.md with step 7
status, file listing, verified test count, rendering examples and semantics, and
the checker warning's limitation. Updated tests/README.md with rendering coverage
and appended this record. No dependency changes, Git commits, uploads, registration,
TimeLimit wrapping, or demo changes were made. Step 7 is complete. Stop before
step 8 and wait for explicit user instruction.

## Step 8: registration and the 500-step time limit

### Authorization and inspection

The user authorized step 8 only, documentation afterward, and a stop before step 9.
Read package initialization, the environment implementation, README status, and
log tail. Searched for workspace AGENTS.md files outside Git and .venv; none found.

### Implementation completed

- Added Gymnasium register to package initialization with the exact required ID
  IcyGridWorld-v0, entry_point icy_gridworld.env:IcyGridWorldEnv, and
  max_episode_steps=500. Importing icy_gridworld now performs registration.
- Used Gymnasium's existing TimeLimit wrapper through gym.make; no custom time
  limit or base-environment truncation logic was introduced. The base transition
  kernel, rewards, reset, and step implementations remain unchanged.
- Updated the package docstring. Package imports now depend on the declared
  Gymnasium dependency, unlike the earlier utility-only stages.
- Added six tests in tests/test_registration.py: exact spec and wrapper checks,
  fresh subprocess import followed by gym.make, 500-step truncation and reset,
  early-goal termination, simultaneous goal/truncation at transition 500, and
  Gymnasium's full checker with the registered spec.

### Verification results

Ran `.venv/Scripts/python.exe -B -m pytest -q -p no:cacheprovider`: all 38 tests
passed without warnings. The fresh subprocess successfully imported the package,
created the registered environment, verified the limit, reset, and closed it.

Boundary tests advance wrapper and base counters through actual step calls with
a deterministic injected RNG. Confirmed transitions 1-499 do not truncate,
transition 500 truncates without termination when blocked at the start, reset
restarts the counter/limit, and early goal entry terminates without truncation.
For simultaneous flags, executed 499 blocked transitions, changed only the test
position to a goal neighbor, then reached the goal on transition 500: reward
100.0, terminated=True, truncated=True, info steps=500. Position/RNG injection
is test-only. Existing tests still verify no truncation in the unwrapped base.

The full Gymnasium check_env call on the registered unwrapped instance passed,
including automatic render-mode checks and close checks. The missing-spec warning
from step 7 is resolved. No dependencies were changed.

### Documentation and stopping point

After implementation and passing checks, updated README.md with step 8 status,
new files and test count, gym.make usage, unwrapped exact-query access, reset
requirements, and termination/truncation semantics. Updated tests/README.md with
new coverage and appended this record. No comprehensive step 9 review, demo
changes, Git commits, or uploads were performed. Step 8 is complete. Stop before
step 9 and await explicit user instruction.

## Step 9: comprehensive correctness and reproducibility verification

### Authorization and review

The user authorized step 9 only, documentation after completion, and a stop before
step 10. Read environment-setup, registration, and step tests plus README status.
Searched for workspace AGENTS.md outside .git/.venv; none found. Reviewed existing
coverage against the agreed step 9 checklist and the PDF requirements already
read in this conversation. Existing tests cover map/encoding, all movement and
transition combinations, invalid inputs, reset, rewards, time limits, rendering,
and the full Gymnasium checker. No production-code defect was identified.

### Changes made

Added tests/test_integration.py with three meaningful integration checks:

- Three registered episodes in two newly created environments, comparing full
  observations/rewards/flags/info and separately seeded action sequences. The
  first reset uses a fixed seed; later resets use None. Each episode runs until
  termination or truncation, checking the counter after every transition.
- Compare two environments receiving identical requested actions while only one
  performs rendering, exact queries for all actions, and action-space sampling.
  This verifies that these operations do not perturb the environment slip stream.
- Sample 20,000 executed directions for each of four requested actions (80,000
  draws), compare against explicit 0.8/0.1/0.1 tables, and disallow backward slips.
  Use a fixed seed and six binomial standard deviations plus one sample of
  rounding for each frequency tolerance. Existing 60,000 next-state samples
  remain, yielding 140,000 stochastic draws in the full suite.

No production modules or dependencies were changed. Existing tests provide the
deterministic exhaustive coverage; the new tests address cross-component and
all-action sampling coverage without replacing those checks.

### Verification results

Ran `.venv/Scripts/python.exe -B -m pytest -q -p no:cacheprovider -W error`:
all 41 tests passed with warnings treated as errors. This includes the complete
registered Gymnasium environment checker, 1,404 movement pairs, 1,408 exact
state/action pairs, 4,212 sampled-outcome branches, rendering at all 352 agent
positions, reward and info contracts, and all time-limit boundary cases.
Ran pip check: no broken requirements. Tests used the existing Python 3.12.6,
Gymnasium 1.3.0, and pytest 8.4.2 virtual environment. Results are evidence for
that configuration; execution on Python 3.10 and standalone builds remain untested.

### Documentation and stopping point

After verification, updated README.md with step 9 status, 41-test count, and the
new integration-test file. Added a consolidated checklist-to-test coverage table,
strict test command, statistical rationale, and limitations to tests/README.md.
Appended this record. No demo implementation, general step 10 documentation work,
Git commit, upload, or submission was performed. Step 9 is complete; stop before
step 10 and wait for explicit user instruction.

## Step 10: runnable demonstration and usage documentation

### Authorization and inspection

The user authorized step 10 only, documentation afterward, and a stop before
step 11. Read demo.py, the full README, and log tail. Searched for workspace
AGENTS.md outside .git/.venv; none found. The existing demo was a placeholder.

### Implementation completed

- Replaced the placeholder with a random-policy CLI using gym.make and the
  registered default 500-step wrapper. No environment implementation was changed.
- Added --episodes (positive, default 1), --seed (nonnegative, default 123),
  --action-seed (nonnegative, default 456), and --render-mode (none/ansi/human).
- Seeded the action space separately; seeded the first environment reset and used
  seed=None on subsequent episodes. Sampled actions until either episode flag
  becomes true, and used a context manager to close the environment.
- Printed episode steps, undiscounted reward sum, final observation/position,
  termination and truncation flags. ANSI prints final episode grids; human mode
  delegates automatic per-reset/per-step printing to the environment.
- Added three demo tests for real-run reproducibility, CLI validation, and
  stopping on either/both flags plus reset sequencing, seeding, and closure.

### Verification results

Ran `.venv/Scripts/python.exe -B -m pytest -q -p no:cacheprovider -W error`:
all 44 tests passed. Ran demo.py directly with defaults: 500 steps, reward -500.0,
observation 257, position (12,17), terminated False, truncated True. Ran the
documented two-episode ANSI command with seeds 123/456: both episodes truncated
at 500 with reward -500.0; second final observation 188, position (9,8). Inspected
the printed final grids. The automated test repeats that real two-episode command
in-process and verifies identical output. Mock-based tests separately exercise
goal termination and simultaneous flags, without claiming the random demo reaches
gold in the observed runs. Human rendering itself is covered by existing tests.

### Documentation completed after verification

Updated README.md with step 10 status, file list, 44-test count, strict test command,
corrected aggregate 140,000 sampling coverage, and default/multi-episode/render
demo commands. Documented all options, random-policy limitations, independent RNG
seeds and continuation, closing, sample output, and termination versus truncation.
Explained gamma=0.99 for a learning algorithm and distinguished discounted return
from the demo's undiscounted sum. Existing installation, encoding, map, exact-query,
and rendering documentation was retained. Updated tests/README.md and this log.

No dependencies or environment modules were changed. No fresh-install audit,
distribution build, Git commits, GitHub upload, or course submission was performed.
Those final preparation activities remain outside this authorized step. Step 10
is complete; stop before step 11 and await explicit user instruction.

## Step 11 in progress and additional desktop viewer request

Inspected Git status, remotes, history, packaging, and ignore rules. There is no
remote and no existing commit history; GitHub CLI is unavailable. Asked the user
for a GitHub destination and course submission URL (and instructor username if
private access is needed). Publishing/submission cannot be completed without
those details. Earlier meaningful development commits cannot be reconstructed
honestly as if they had been made during development.

While final preparation was in progress, the user requested a GUI. Added gui.py,
a separate Tkinter desktop viewer using the registered, wrapped environment.
Includes a 20x20 canvas with row/column labels, rocks, gold, explorer, start marker,
direction buttons/arrow keys, seeded reset, random play/pause at 250ms intervals,
and live step/reward/action/slip/collision/termination/truncation information.
Both end flags stop playback and disable movement until reset. Rendering modes
of the underlying environment were not changed. Tkinter 8.6 is available locally.

Ran a withdrawn-window smoke check exercising construction, manual movement,
random playback, pause, reset, and close; passed. Launched the desktop viewer
using pythonw.exe through Start-Process. Updated README with the launch command
and controls. No GUI screenshot or visual inspection was performed.

Created a separate clean virtual environment in ignored tmp/final-check, installed
requirements.txt successfully, and ran all 44 tests with warnings treated as
errors: passed. Ran the default demo successfully with the documented result;
pip check found no broken requirements. The original .venv also passed all 44
tests after the GUI addition. Reviewed the candidate tracked-file list: only
source, tests, configuration, and documentation; virtual environments and generated
files are excluded. Local verification is complete. GitHub publishing, instructor
access, and course submission remain pending destination details. Step 11 is not
fully complete, and no external submission is claimed.
