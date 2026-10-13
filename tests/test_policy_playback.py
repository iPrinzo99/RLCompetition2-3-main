"""Playback must request saved actions, rather than explore randomly."""
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import Mock
import unittest
import numpy as np
import gymnasium as gym
from policy_playback import load_policy,requested_action,POLICY_FILES
from gui import GridViewer

class PlaybackTests(unittest.TestCase):
    def test_all_saved_modes_and_planner_agreement(self):
        policies=[load_policy(name) for name in POLICY_FILES if name!='Random baseline']
        self.assertEqual(len(policies),4)
        np.testing.assert_array_equal(policies[0],policies[1])
        self.assertIsNone(load_policy('Random baseline'))
    def test_saved_action_does_not_sample(self):
        space=Mock();space.sample.side_effect=AssertionError('Random action requested')
        policy=load_policy()
        self.assertEqual(requested_action(policy,380,space),1)
        space.sample.assert_not_called()
    def test_random_is_explicit(self):
        space=Mock();space.sample.return_value=3
        self.assertEqual(requested_action(None,380,space),3)
        space.sample.assert_called_once()
    def test_corrupt_or_missing_policy_fails_instead_of_random(self):
        with TemporaryDirectory() as folder:
            with self.assertRaises(FileNotFoundError):load_policy(results_dir=folder)
            np.savez(Path(folder)/'value_iteration.npz',policy=np.full(400,-1))
            with self.assertRaises(ValueError):load_policy(results_dir=folder)
    def test_gui_tick_uses_current_observation_and_saved_policy(self):
        viewer=GridViewer.__new__(GridViewer);viewer.running=True;viewer.timer=None
        viewer.policy=load_policy();viewer.observation=380;viewer.env=Mock()
        viewer.env.action_space.sample.side_effect=AssertionError('GUI sampled random action')
        viewer.step=Mock();viewer.root=Mock()
        viewer.tick();viewer.step.assert_called_once_with(1)
        viewer.env.action_space.sample.assert_not_called()
    def test_gui_single_step_uses_saved_policy(self):
        viewer=GridViewer.__new__(GridViewer);viewer.done=False;viewer.policy=load_policy()
        viewer.observation=380;viewer.env=Mock();viewer.stop=Mock();viewer.step=Mock()
        viewer.policy_step();viewer.step.assert_called_once_with(1)
        viewer.env.action_space.sample.assert_not_called()
    def test_optimal_playback_reaches_goal_without_action_exploration(self):
        policy=load_policy()
        for seed in [123,456,789]:
            env=gym.make('IcyGridWorld-v0');obs,_=env.reset(seed=seed)
            env.action_space.sample=Mock(side_effect=AssertionError('Exploration used'))
            for _ in range(500):
                obs,r,term,trunc,_=env.step(requested_action(policy,obs,env.action_space))
                if term or trunc:break
            self.assertTrue(term);self.assertEqual(obs,19);env.close()

if __name__=='__main__':unittest.main()
