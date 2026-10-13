"""Control correctness tests beyond the unchanged Competition 1 suite."""
import unittest
import numpy as np
from competition import Model, value_iteration, policy_iteration, train, GAMMA, td_target

class ControlTests(unittest.TestCase):
    def test_planning_reference_and_greedy_policy(self):
        m=Model();v,vi,info=value_iteration(m);w,pi,pinfo=policy_iteration(m)
        np.testing.assert_allclose(v,w,atol=1e-8,rtol=0)
        self.assertLess(info['residual'],1e-8);self.assertLess(pinfo['residual'],1e-8)
        np.testing.assert_array_equal(vi[m.active],pi[m.active])
        np.testing.assert_allclose(m.evaluate(vi),v,atol=1e-8,rtol=0)
        self.assertAlmostEqual(v[m.start],26.282822174,places=7)
        self.assertEqual(v[m.goal],0)
    def test_model_rewards_and_merged_collisions(self):
        m=Model();i=m.lookup[380]
        self.assertEqual(len(m.ids),352);self.assertEqual(int(m.active.sum()),351)
        np.testing.assert_allclose(m.prob.sum(axis=2),1)
        self.assertAlmostEqual(m.r[m.lookup[18],1],79.8)
        p={int(m.ids[n]):float(q) for n,q in zip(m.next[i,2],m.prob[i,2]) if q>0}
        self.assertEqual(p,{380:0.9,381:0.1})
    def test_learning_reproducibility_and_budget(self):
        for alg in ['sarsa','q_learning']:
            q,n,_,_=train(alg,7,2000)
            qq,nn,_,_=train(alg,7,2000)
            np.testing.assert_array_equal(q,qq);np.testing.assert_array_equal(n,nn)
            self.assertEqual(n.sum(),2000);self.assertTrue(np.isfinite(q).all())
            np.testing.assert_array_equal(q[19],np.zeros(4))
    def test_targets_distinguish_behavior_and_terminal_cutoff(self):
        q=np.zeros((400,4));q[7]=[10,20,30,40]
        # A nonterminal final observation must retain its bootstrap after a cutoff.
        self.assertAlmostEqual(td_target('sarsa',q,7,-1,False,0),8.9)
        self.assertAlmostEqual(td_target('q_learning',q,7,-1,False,0),38.6)
        for alg in ['sarsa','q_learning']:
            self.assertEqual(td_target(alg,q,7,100,True,0),100)

    def test_goal_continuation_and_cap(self):
        m=Model();v,p,_=value_iteration(m)
        q=m.q(v);self.assertTrue(np.all(q[m.goal]==0))
        capped,success=m.capped(p)
        self.assertAlmostEqual(capped,v[m.start],places=7)
        self.assertGreater(success,.999)

if __name__=='__main__':unittest.main()
