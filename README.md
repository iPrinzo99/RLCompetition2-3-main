# RLCompetition2-3-main
<<<<<<< HEAD

Reproducible implementation and investigation of policy iteration, value iteration,
SARSA, and Q-learning on the exact CIS 5930 Competition 1 Icy Grid World.
The original `icy_gridworld` implementation is preserved. The viewer and demo
now play saved policies; the baseline tests remain, with demo fixtures adapted
to policy playback. Added control methods use the original environment without changing
its map, transition probabilities, rewards, or 500-step external time limit.

## Watch a saved policy

From this folder, with the project Python environment active:

```sh
python gui.py
```

Choose **Value iteration (optimal)** or **Policy iteration (optimal)**, then press
**Play policy** or **Policy step**. The default is value iteration, and the grid
shows requested-action arrows. SARSA and Q-learning selections replay the saved
learned policies with exploration disabled; they are not guaranteed optimal.
**Random baseline** is available only as an explicit selection. Ice still causes
perpendicular slips 20 percent of the time, so a path can vary under optimal play.

For text playback:

```sh
python demo.py --policy value_iteration --episodes 3 --render-mode human
python demo.py --policy policy_iteration --episodes 3
python demo.py --policy sarsa --episodes 3
python demo.py --policy q_learning --episodes 3
python demo.py --policy random --episodes 1
```

The learned GUI/demo selections use decay-exploration training seed 0. The seed
field controls the episode's ice randomness, not the saved training policy.
`competition.py` trains and evaluates policies; it does not animate the viewer.
No retraining is required to use the saved results.

## Install and run

Python 3.10 or later is required. From this folder:

```sh
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell alternative: .\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
python competition.py --budget 1000000 --seeds 10 --eval-episodes 1000 --output results
python analyze_results.py
```

`competition.py` saves intermediate results after every learning run. Rerunning it
replaces results in the specified output folder. A short smoke experiment is:

```sh
python competition.py --budget 10000 --seeds 2 --eval-episodes 100 --output smoke_results
```

For figures and report regeneration, optionally run `python -m pip install -r requirements-report.txt`, then `python visualize_results.py` and `python build_report.py`.
For closest numeric reproduction, use Python 3.12 and `requirements-reproduce.txt` in place of `requirements.txt`. The included figure builder uses the macOS Arial font path; adjust `FONT` to an
available TrueType font on other operating systems. Figures and the report are
already included and Pillow is not needed for training or analysis.

## Model and learning settings

- Exact 20 by 20 map with 48 obstacles, 352 states, and no hazards.
- Start `(19, 0)`, goal `(0, 19)`; action IDs up 0, right 1, down 2, left 3.
- Intended direction probability 0.80; each perpendicular direction 0.10.
- Collision self-loop; reward -1 except +100 on goal entry; gamma 0.99.
- Registered environment `IcyGridWorld-v0`; 500-step TimeLimit is external.
- Planning uses the exact kernel. VI tolerance is 1e-10; PI solves evaluation
  systems directly, retaining the current action on a tie.
- Learning calls the original registered Gymnasium environment for every step.
  Both algorithms use zero initialization and constant alpha 0.1.
- Fixed epsilon is 0.10. The decay setting decreases linearly from 1.0 to 0.02
  during the first 80 percent of the transition budget, then stays at 0.02.
- Both termination and truncation end a rollout and trigger reset, but only
  termination suppresses bootstrapping. SARSA samples its next action at the
  final observation before resetting.

The saved experiment uses seeds 0 through 9, 1,000,000 transitions for every
method/setting/seed, and 1,000 held-out evaluation episodes per frozen policy.
The action RNG uses seed + 100000; the environment uses the training seed and
continues its RNG stream on reset. Evaluation seeds are 200000 through 200999.
Greedy evaluation disables exploratory action choices but keeps ice slipping.
Only steps 10,000, 50,000, and 1,000,000 are checkpointed in the learning curves.

## Evidence and output files

- `RLCompetition2-3-main.docx`: editable analysis with equations, policy maps,
  measured results, and limitations.
- `competition.py`: exact planning, tabular learning, scoring, and evaluations.
- `analyze_results.py`: evaluates saved epsilon-greedy behavior policies exactly
  and computes the constrained epsilon reference for 0.10 and 0.02.
- `results/results.json`, `results/summary.csv`: measured settings and outcomes.
- `results/*.npz`: saved values, Q tables, policies, and visitation counts.
  Policy IDs for obstacles and the goal are -1; reference arrays use state_ids.
- `figures/`: policy comparison and learning curves.
- `SOURCE_MANIFEST.json`: hashes for the preserved original environment files.
- `TEAM_README.md`, `TEAM_AI_LOG.md`: unchanged documentation from the baseline.
- `AI_LOG.md`: record of the new work and verification.

PI and VI provide a validated optimal-value reference. Finite-budget learned
policies are evaluated against that reference and are not automatically called
optimal. The fixed learning rate and nonzero exploration floor do not establish
asymptotic convergence. Runtime measures are local observations, not universal
algorithm rankings. Exact policy evaluation describes the underlying discounted
MDP; 500-step rollout return and success rate describe a separate capped metric.

No upload or submission is performed by the experiment scripts.
=======
Repository housing reinforcement learning algorithms, training pipelines, and experimental runs for competition tasks.
>>>>>>> d307a0f4b72893f372ed62479250e9594fb50243
