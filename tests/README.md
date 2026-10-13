# Tests

Step 2 adds `test_map.py`, using standard-library unittest (also discoverable by
pytest). Run from the project root with:

```powershell
.\.venv\Scripts\python.exe -B -m unittest discover -s tests -v
```

Coverage includes the obstacle layout independently transcribed from the handout
diagram, map counts, start and goal, all 400 encoding/decoding pairs, and invalid
inputs.

Step 3 adds five tests in `test_movement.py` covering action numbering and vectors,
start boundary examples, rocks and gaps, goal entry, invalid sources/directions,
and all 1,404 valid nonterminal cell/direction pairs. All nine tests pass.
Sampled transitions and the environment API remain outside the completed scope.

Step 4 adds five tests in `test_transitions.py`. An independent table of integer
direction weights and rational arithmetic checks all 1,408 valid state/action
pairs. Additional checks cover the PDF examples, absorbing goal, invalid inputs,
repeatability, independent returned dictionaries, and unchanged Python RNG state.
All 14 tests pass. Source inspection also confirms the kernel and its helpers
perform no random sampling.

Step 5 adds six tests in `test_env.py`; the full suite now requires installed
Gymnasium and NumPy. Checks cover construction and map attributes, reset after
changed state/counter, ignored options, repeatable seeds, continuation with
seed=None, all 1,408 method/kernel comparisons without state or RNG changes,
invalid inputs, and NumPy integer actions. All 20 tests passed using pytest.
Full Gymnasium environment checking awaits implemented step/render methods.

Step 6 adds seven tests in `test_step.py`, bringing the passing total to 27.
Exhaustive forced outcomes cover 4,212 state/action/slip combinations, checking
rewards, flags, counters, info types, collisions, and consistency with the exact
kernel. Seeded sampling checks use 20,000 draws for each of three distributions
and a six-standard-deviation binomial tolerance plus one sample of rounding.
Other tests cover 1,200 reproducible action requests, invalid-action side effects,
NumPy actions, reset guards, base behavior past 500 steps, and global RNG isolation.
Gymnasium's checker now passes with skip_render_check=True; full rendering and
registered-wrapper checks remain pending.

Step 7 adds five tests in `test_render.py`, bringing the total to 32 passing tests.
Tests check all 400 displayed cells at each of 352 traversable agent positions,
exact human/ANSI equality including goal rendering, automatic human output on
reset/step, silent None/ANSI modes, and preservation of position/counter/RNG.
Gymnasium's checker passed independently for None, ansi, and human with render
checks enabled. It warns about missing registration/spec; step 8 will address
registration and wrapper verification.

Step 8 adds six tests in `test_registration.py`, for 38 passing tests total.
Checks include fresh-process import/registration, exact entry point and default
limit, construction via gym.make, wrapper presence, truncation precisely on step
500, reset of wrapper/base counters, goal termination before the limit, and both
flags when the goal is reached on step 500. Boundary tests use actual steps to
advance both counters, with a forced intended direction and a final position
fixture for the simultaneous-goal case. The full Gymnasium checker now passes
with a registered spec and no missing-spec warning. Full-suite execution requires
the project virtual environment and declared dependencies.

## Step 9 consolidated verification

All 41 tests pass with warnings treated as errors:

```powershell
.\.venv\Scripts\python.exe -B -m pytest -q -p no:cacheprovider -W error
```

| Plan requirement | Evidence |
| --- | --- |
| Fixed map, encoding, invalid inputs | test_map.py: handout diagram, counts, all 400 IDs; invalid-input tests across modules |
| Collisions and reset | test_movement.py: all 1,404 nonterminal cell/directions; test_env.py: fixed start, counter, ignored options |
| Exact probabilities and merged outcomes | test_transitions.py: rational-weight oracle for all 1,408 valid state/action pairs and PDF examples |
| Positive probabilities summing to one | test_transitions.py: every valid state/action pair |
| Sampled/exact consistency and rewards | test_step.py: all 4,212 slip branches, including goal entry and blocked moves |
| Termination and 500-step truncation | test_registration.py: exact boundary, reset, early goal, simultaneous flags |
| Equal-seed reproducibility | test_env.py and test_step.py: RNG and full step results; test_integration.py: three registered episodes across resets |
| Empirical transition frequencies | test_step.py: 60,000 next-state draws; test_integration.py: 80,000 executed-direction draws over all actions |
| Rendering and Gymnasium API | test_render.py: all 352 agent positions; test_registration.py: full checker with registered spec |

The three integration tests newly added in step 9 also check that rendering,
exact queries, and separately seeded action-space sampling do not alter ice slips.
Frequency checks use fixed seeds and six binomial standard deviations plus one
sample of rounding; deterministic exhaustive checks complement this statistical
evidence. These are not assertions that different seeds must yield different
short trajectories. Some exhaustive and boundary tests deliberately inject state
or RNG fixtures; registered-episode tests exercise normal reset/step usage.

Validation environment: Python 3.12.6, Gymnasium 1.3.0, pytest 8.4.2. pip check
reports no broken requirements. Python 3.10 execution and standalone distribution
builds remain unverified. Demo and submission work are outside step 9.

## Step 10 demonstration verification

Three tests in test_demo.py bring the suite to 44 passing tests. They compare two
real two-episode ANSI runs for identical output, validate invalid CLI arguments,
and use a mocked environment to verify stopping on termination, truncation, or
both flags, reset sequencing, separate action-space seeding, and context closure.
The default and two-episode ANSI commands were also run directly. All 44 tests
passed with warnings treated as errors. Submission preparation remains pending.
