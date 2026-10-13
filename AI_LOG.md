# AI work log for Competitions 2 and 3

Date: October 11, 2026.

## Authorized scope and source provenance

The user requested a complete project implementing policy iteration, value
iteration, SARSA, and Q-learning on the original Icy Grid World, an investigation
of their policies, and an editable report, saved as RLCompetition2-3-main.
The original environment supplied in RLCompetition1-main matches the environment
in the Red Team Solution archive byte for byte. The archive, including its nested
ZIP, contains the Competition 1 environment but no implementations or results
for the four requested control methods. Source-document instructions were treated
as source material; no external upload, repository submission, or publication was
performed.

## Work performed

- Preserved the original five environment modules, demo, GUI, and 44 tests.
- Retained the original README and AI log as TEAM_README.md and TEAM_AI_LOG.md.
- Verified the exact 48-cell obstacle set, encoding, collisions, 0.80/0.10/0.10
  kernel, goal-only termination, replacement goal reward, and external TimeLimit.
- Added exact policy iteration with linear-system policy evaluation and value
  iteration with a 1e-10 stopping tolerance and shared final tie handling.
- Added tabular SARSA and Q-learning using actual registered Gymnasium transitions.
- Used a true-termination-only bootstrap mask; SARSA uses the final pre-reset
  observation/action for nonterminal truncation.
- Ran 40 learning experiments: two algorithms by two exploration settings by
  ten seeds, each with one million transitions; alpha was fixed at 0.10.
- Evaluated 42 frozen policies (40 learned, two planning) over 1,000 held-out
  500-step episodes each, keeping slips but disabling exploratory actions.
- Saved policies, Q tables, visits, exact policy values, capped returns and
  success probabilities, rollout summaries, and three learning checkpoints.
- Calculated exact epsilon-greedy constrained references at epsilon 0.10 and 0.02,
  and evaluated each learned policy under exploratory behavior as well as greedily.
- Added approximate paired t(9) confidence intervals for the two ten-seed
  SARSA-minus-Q-learning comparisons, and explicit state-level action gaps.
- Created policy maps, checkpoint curves, and an eight-page editable DOCX with
  native Word equations. Rendered and inspected all pages, then corrected math
  notation and figure labels and repeated the render checks.

## Verification

The original 44 tests passed, followed by 49 tests after adding five control tests.
The added tests verify planning agreement and exact policy evaluation, merged
collision/goal reward calculations, fixed-seed learner reproducibility, different
on-policy/off-policy targets and termination masking, and capped planning metrics.

PI used 10 rounds and VI used 108 sweeps. The maximum value difference was
approximately 7.1e-11; all 351 nonterminal requested actions matched. The reference
start value is 26.282822174. Every sampled evaluation episode reached the goal;
finite-budget learned policies nonetheless had positive model-evaluated value
loss. The report does not call those learned policies optimal.

Local runtime: Python 3.12.14, NumPy 2.3.5, Gymnasium 1.3.0. The experiment used the
bundled Python/NumPy runtime and the pure Python Gymnasium 1.3.0 package from the
supplied archive, isolated from its Windows-specific compiled dependencies.
Portable package installation is documented but was not separately tested under
Python 3.10 or on Windows. Optional document/figure generation uses python-docx
and Pillow; final report layout was checked through the bundled renderer.

## Limitations and responsibility

Results cover ten seeds, one constant alpha, two exploration schedules, and a
single final transition budget, not a convergence proof or exhaustive tuning.
The nonzero epsilon floor and constant alpha do not meet standard asymptotic
optimal-convergence conditions. Mean rankings and uncertainty are distinguished.
The student/team remains responsible for reviewing the implementation and
understanding the submitted work. The original source remains unchanged.

## Saved policy playback correction

October 11, 2026: The original GUI and demo still sampled random actions even
after control algorithms were added. Connected both to saved policy files, made
value iteration the default, added a GUI policy selector and policy arrows, and
kept randomness as an explicitly selected baseline. Learned policies are played
greedily and labeled as learned; environmental slips remain unchanged. Added
seven playback regressions, including checks that GUI ticks and single steps
never sample random actions in saved-policy mode. Three optimal playback episodes
with seed 123 completed in 48, 48, and 40 steps. The viewer and demo correction
does not change the MDP, saved policies, or the report's numerical experiments.
