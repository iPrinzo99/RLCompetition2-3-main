"""Load saved policies and select actions without training exploration."""
from pathlib import Path
import numpy as np
from icy_gridworld import obstacles,goal

POLICY_FILES = {
    'Value iteration (optimal)': 'value_iteration.npz',
    'Policy iteration (optimal)': 'policy_iteration.npz',
    'SARSA (learned, decay seed 0)': 'sarsa_decay_seed0.npz',
    'Q-learning (learned, decay seed 0)': 'q_learning_decay_seed0.npz',
    'Random baseline': None,
}
CLI_POLICIES = dict(zip(('value_iteration','policy_iteration','sarsa','q_learning','random'),POLICY_FILES))
DEFAULT_POLICY = 'Value iteration (optimal)'

def load_policy(label=DEFAULT_POLICY, results_dir=None):
    if label not in POLICY_FILES:raise ValueError(f'Unknown policy: {label}')
    filename=POLICY_FILES[label]
    if filename is None:return None
    directory=Path(results_dir) if results_dir is not None else Path(__file__).resolve().parent/'results'
    path=directory/filename
    if not path.is_file():raise FileNotFoundError(f'Saved policy missing: {path}. Restore the included results folder or run competition.py.')
    with np.load(path,allow_pickle=False) as data:
        if 'policy' not in data:raise ValueError(f'No policy array in {path}')
        raw=data['policy']
        if raw.shape==(400,):policy=raw.copy()
        elif raw.shape==(352,) and 'state_ids' in data:
            ids=data['state_ids']
            if ids.shape!=(352,) or not np.issubdtype(ids.dtype,np.integer) or len(set(ids.tolist()))!=352 or np.any((ids<0)|(ids>=400)):
                raise ValueError(f'Invalid state IDs in {path}')
            policy=np.full(400,-1,dtype=raw.dtype);policy[ids]=raw
        else:raise ValueError(f'Expected 400 actions or 352 actions with state IDs in {path}')
    active=np.array([20*r+c for r in range(20) for c in range(20) if (r,c) not in obstacles and (r,c)!=goal])
    if not np.issubdtype(policy.dtype,np.integer) or np.any((policy[active]<0)|(policy[active]>3)):
        raise ValueError(f'Policy has invalid or missing actions in {path}')
    return policy.astype(int)

def requested_action(policy,observation,action_space):
    if policy is None:return int(action_space.sample())
    action=int(policy[observation])
    if action not in (0,1,2,3):raise ValueError(f'No playable action at observation {observation}')
    return action
