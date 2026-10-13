"""Tabular control and reproducible policy comparisons for Competition 2 and 3.

The unchanged team environment defines every transition and reward. Planning
uses its exact helper; both learners call the registered Gymnasium environment.
"""
from __future__ import annotations
import argparse, json, time, platform
from pathlib import Path
import numpy as np
import gymnasium as gym
import icy_gridworld
from icy_gridworld.env import IcyGridWorldEnv

GAMMA = 0.99

class Model:
    def __init__(self):
        self.ids=np.array([s for s in range(400) if divmod(s,20) not in icy_gridworld.obstacles])
        self.lookup={int(s):i for i,s in enumerate(self.ids)}
        self.goal=self.lookup[19]; self.start=self.lookup[380]
        self.next=np.zeros((352,4,3),dtype=int)
        self.prob=np.zeros((352,4,3))
        self.reward=np.zeros((352,4,3))
        env=IcyGridWorldEnv()
        for i,s in enumerate(self.ids):
            for a in range(4):
                for k,(sp,p) in enumerate(env.transition_probabilities(int(s),a).items()):
                    self.next[i,a,k]=self.lookup[sp];self.prob[i,a,k]=p
                    self.reward[i,a,k]=0 if s==19 else (100 if sp==19 else -1)
        self.r=(self.prob*self.reward).sum(axis=2)
        self.active=np.arange(352)!=self.goal
    def q(self,v):
        q=(self.prob*(self.reward+GAMMA*v[self.next])).sum(axis=2)
        q[self.goal]=0
        return q
    def extract(self,v):
        # Smallest action ID in a tolerance tie; keep the tolerance explicit.
        q=self.q(v);return np.argmax(q>=q.max(axis=1,keepdims=True)-1e-10,axis=1)
    def evaluate(self,policy):
        p=np.zeros((352,352));r=self.r[np.arange(352),policy]
        for k in range(3):np.add.at(p,(np.arange(352),self.next[np.arange(352),policy,k]),self.prob[np.arange(352),policy,k])
        lhs=np.eye(352)-GAMMA*p;lhs[self.goal]=0;lhs[self.goal,self.goal]=1
        r=r.copy();r[self.goal]=0
        return np.linalg.solve(lhs,r)
    def capped(self,policy,limit=500):
        # Exact finite rollout metrics, with terminal zero continuation.
        idx=np.arange(352);prob=self.prob[idx,policy];nxt=self.next[idx,policy]
        ret=np.zeros(352);hit=np.zeros(352);hit[self.goal]=1
        for _ in range(limit):
            ret=self.r[idx,policy]+GAMMA*(prob*ret[nxt]).sum(axis=1);ret[self.goal]=0
            hit=(prob*hit[nxt]).sum(axis=1);hit[self.goal]=1
        return float(ret[self.start]),float(hit[self.start])

def value_iteration(model,tolerance=1e-10):
    t=time.perf_counter();v=np.zeros(352)
    for sweep in range(1,100001):
        new=model.q(v).max(axis=1)
        if np.max(np.abs(new-v))<tolerance:
            v=new;break
        v=new
    else:raise RuntimeError('VI did not converge')
    return v,model.extract(v),{'sweeps':sweep,'seconds':time.perf_counter()-t,'residual':float(np.max(np.abs(model.q(v).max(axis=1)-v)))}

def policy_iteration(model):
    t=time.perf_counter();policy=np.zeros(352,dtype=int)
    for iteration in range(1,1001):
        v=model.evaluate(policy);q=model.q(v);best=q.max(axis=1)
        # Retain a current action if it is tied; final extraction is shared with VI.
        change=q[np.arange(352),policy]<best-1e-10
        if not change.any():break
        policy[change]=np.argmax(q[change],axis=1)
    else:raise RuntimeError('PI did not converge')
    return v,model.extract(v),{'improvement_rounds':iteration,'seconds':time.perf_counter()-t,'residual':float(np.max(np.abs(model.q(v).max(axis=1)-v)))}

def choose(q,s,epsilon,rng):
    return int(rng.integers(4)) if rng.random()<epsilon else int(np.argmax(q[s]))

def td_target(algorithm,q,next_state,reward,terminated,next_action):
    """Only true MDP termination suppresses continuation, never truncation."""
    if terminated:return float(reward)
    continuation=q[next_state,next_action] if algorithm=='sarsa' else q[next_state].max()
    return float(reward+GAMMA*continuation)

def train(algorithm,seed,budget,exploration='fixed',alpha=0.1,checkpoints=()):
    if algorithm not in ('sarsa','q_learning'):raise ValueError(algorithm)
    env=gym.make('IcyGridWorld-v0');rng=np.random.default_rng(seed+100000)
    q=np.zeros((400,4));visits=np.zeros((400,4),dtype=int)
    s,_=env.reset(seed=seed);episodes=successes=timeouts=0; history=[]
    def eps(t):return 0.10 if exploration=='fixed' else max(0.02,1-0.98*t/(0.8*budget))
    a=choose(q,s,eps(0),rng);t0=time.perf_counter()
    for t in range(1,budget+1):
        sp,r,terminated,truncated,_=env.step(a)
        # a' is sampled at final observation, before any reset, for SARSA.
        ap=choose(q,sp,eps(t),rng) if not terminated else 0
        target=td_target(algorithm,q,sp,r,terminated,ap)
        visits[s,a]+=1;q[s,a]+=alpha*(target-q[s,a])
        if terminated or truncated:
            episodes+=1;successes+=int(terminated);timeouts+=int(truncated and not terminated)
            s,_=env.reset();a=choose(q,s,eps(t),rng)
        else:s,a=sp,ap
        if t in checkpoints:
            history.append((t,q.copy()))
    env.close()
    return q,visits,history,{'seconds':time.perf_counter()-t0,'episodes':episodes,'training_goals':successes,'training_timeouts':timeouts,'final_epsilon':eps(budget)}

def rollout(policy,episodes=1000,seed_base=200000):
    env=gym.make('IcyGridWorld-v0');returns=[];lengths=[];success_lengths=[];goals=0
    for e in range(episodes):
        s,_=env.reset(seed=seed_base+e);total=0;discount=1
        for steps in range(1,501):
            s,r,term,trunc,_=env.step(int(policy[s]));total+=discount*r;discount*=GAMMA
            if term or trunc:break
        returns.append(total);lengths.append(steps)
        if term:goals+=1;success_lengths.append(steps)
    env.close()
    return {'episodes':episodes,'goals':goals,'success_rate':goals/episodes,'mean_capped_return':float(np.mean(returns)), 'mean_steps':float(np.mean(lengths)), 'mean_success_steps':float(np.mean(success_lengths)) if success_lengths else None}

def score(model,policy,vstar,qstar):
    v=model.evaluate(policy);capped,hit=model.capped(policy)
    gaps=qstar.max(axis=1)-qstar[np.arange(352),policy]
    return {'value_start':float(v[model.start]),'start_gap':float(vstar[model.start]-v[model.start]),'max_state_gap':float(np.max(vstar-v)), 'exact_capped_return':capped,'exact_success_500':hit,'optimal_actions_fraction':float(np.mean(gaps[model.active]<=1e-6)), 'mean_action_gap':float(gaps[model.active].mean())}

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--budget',type=int,default=1000000);ap.add_argument('--seeds',type=int,default=10);ap.add_argument('--eval-episodes',type=int,default=1000);ap.add_argument('--output',default='results');args=ap.parse_args()
    if args.budget<1 or args.seeds<1 or args.eval_episodes<1:ap.error('budget, seeds, and evaluation episodes must be positive')
    out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
    model=Model();vstar,vi,viinfo=value_iteration(model);vp,pi,piinfo=policy_iteration(model);qstar=model.q(vstar)
    result={'config':{'gamma':GAMMA,'budget':args.budget,'seeds':list(range(args.seeds)),'evaluation_episodes':args.eval_episodes,'alpha':0.1,'fixed_epsilon':0.1,'decay':'linear 1.0 to 0.02 over first 80% of transition budget, then 0.02','tie_rule':'smallest action ID; planner tolerance 1e-10','python':platform.python_version(),'numpy':np.__version__,'gymnasium':gym.__version__},'planning':{},'runs':[]}
    for name,pol,info in [('policy_iteration',pi,piinfo),('value_iteration',vi,viinfo)]:
        full=np.full(400,-1,dtype=int);full[model.ids]=pol;full[19]=-1
        met=score(model,pol,vstar,qstar);met.update(info);met['rollout']=rollout(full,args.eval_episodes)
        result['planning'][name]=met;np.savez(out/(name+'.npz'),policy=full,value=model.evaluate(pol),state_ids=model.ids)
    result['planning_agreement']={'max_value_difference':float(np.max(np.abs(vstar-vp))),'action_agreement':float(np.mean(pi[model.active]==vi[model.active]))}
    np.savez(out/'reference.npz',state_ids=model.ids,value=vstar,q=qstar,policy=vi)
    checkpoints=sorted(set([min(10000,args.budget),min(50000,args.budget),args.budget]))
    for exploration in ['fixed','decay']:
        for alg in ['sarsa','q_learning']:
            for seed in range(args.seeds):
                q,visits,history,info=train(alg,seed,args.budget,exploration,checkpoints=checkpoints)
                pol=q[model.ids].argmax(axis=1);met=score(model,pol,vstar,qstar)
                full=q.argmax(axis=1);full[np.setdiff1d(np.arange(400),model.ids)]=-1;full[19]=-1
                met.update(info);met['rollout']=rollout(full,args.eval_episodes)
                met['visited_pairs']=int((visits[model.ids][model.active]>0).sum());met['zero_visit_pairs']=1404-met['visited_pairs'];met['min_visits']=int(visits[model.ids][model.active].min())
                curves=[]
                for steps,qq in history:
                    pp=qq[model.ids].argmax(axis=1);curves.append({'steps':steps,**score(model,pp,vstar,qstar)})
                run={'algorithm':alg,'exploration':exploration,'seed':seed,'metrics':met,'checkpoints':curves};result['runs'].append(run)
                np.savez(out/f'{alg}_{exploration}_seed{seed}.npz',q=q,visits=visits,policy=full)
                (out/'results.json').write_text(json.dumps(result,indent=2))
                print(f'{alg} {exploration} seed {seed}: gap={met["start_gap"]:.4f}, value={met["value_start"]:.4f}, optimal actions={met["optimal_actions_fraction"]:.3f}',flush=True)
    (out/'results.json').write_text(json.dumps(result,indent=2))
    print('Finished',flush=True)

if __name__=='__main__':main()
