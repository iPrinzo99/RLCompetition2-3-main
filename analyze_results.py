"""Exact stochastic behavior-policy evaluation and summary of saved runs."""
from pathlib import Path
import json,csv
import numpy as np
from competition import Model,GAMMA

def evaluate_distribution(m,dist):
    p=np.zeros((352,352))
    for a in range(4):
        for k in range(3):np.add.at(p,(np.arange(352),m.next[:,a,k]),dist[:,a]*m.prob[:,a,k])
    r=(dist*m.r).sum(axis=1);lhs=np.eye(352)-GAMMA*p
    lhs[m.goal]=0;lhs[m.goal,m.goal]=1;r[m.goal]=0
    return np.linalg.solve(lhs,r)

def epsilon_distribution(policy,epsilon):
    dist=np.full((352,4),epsilon/4);dist[np.arange(352),policy]+=1-epsilon;return dist

def epsilon_reference(m,epsilon):
    v=np.zeros(352)
    for _ in range(100000):
        q=m.q(v);new=(1-epsilon)*q.max(axis=1)+epsilon*q.mean(axis=1)
        if np.max(np.abs(new-v))<1e-10:v=new;break
        v=new
    policy=np.argmax(m.q(v),axis=1)
    return v,policy

def diagnostics(m,r):
    ref=np.load(Path(__file__).parent/'results/reference.npz');qstar=ref['q'];pi=ref['policy'];idx=np.arange(352)
    p=np.zeros((352,352))
    for k in range(3):np.add.at(p,(idx,m.next[idx,pi,k]),m.prob[idx,pi,k])
    e=np.zeros(352);e[m.start]=1;occupancy=np.linalg.solve(np.eye(352)-GAMMA*p.T,e)
    policies={}
    for alg in ['sarsa','q_learning']:
        group=sorted([x for x in r['runs'] if x['algorithm']==alg and x['exploration']=='fixed'],key=lambda x:x['metrics']['start_gap'])
        seed=group[len(group)//2]['seed']
        policies[alg]=np.load(Path(__file__).parent/f'results/{alg}_fixed_seed{seed}.npz')['policy'][m.ids]
    diff=(policies['sarsa']!=policies['q_learning'])&m.active
    loss=np.maximum(qstar.max(axis=1)-qstar[idx,policies['sarsa'].clip(0)],qstar.max(axis=1)-qstar[idx,policies['q_learning'].clip(0)])
    candidates=np.where(diff)[0];candidates=candidates[np.argsort((occupancy*loss)[candidates])[::-1]][:3]
    states=[{'state':list(divmod(int(m.ids[i]),20)),'reference_action':int(pi[i]),'sarsa_action':int(policies['sarsa'][i]),'q_learning_action':int(policies['q_learning'][i]),'reference_q':qstar[i].tolist(),'sarsa_action_gap':float(qstar[i].max()-qstar[i,policies['sarsa'][i]]),'q_learning_action_gap':float(qstar[i].max()-qstar[i,policies['q_learning'][i]])} for i in candidates]
    comparisons={}
    # t(9) interval for the fixed ten-seed saved experiment; general df requires
    # a t quantile implementation and is deliberately omitted for other counts.
    for mode in ['fixed','decay']:
        values={alg:{x['seed']:x['metrics']['value_start'] for x in r['runs'] if x['algorithm']==alg and x['exploration']==mode} for alg in ['sarsa','q_learning']}
        seeds=sorted(set(values['sarsa'])&set(values['q_learning']))
        delta=np.array([values['sarsa'][i]-values['q_learning'][i] for i in seeds]);item={'sarsa_minus_qlearning_mean':float(delta.mean())}
        if len(delta)==10:
            half=2.262*delta.std(ddof=1)/np.sqrt(10);item['paired_t_95_interval']=[float(delta.mean()-half),float(delta.mean()+half)]
        comparisons[mode]=item
    return {'states':states,'comparisons':comparisons}

def main():
    path=Path(__file__).parent/'results';m=Model();r=json.loads((path/'results.json').read_text())
    r['epsilon_references']={}
    for eps in [.1,.02]:
        v,p=epsilon_reference(m,eps);greedy=evaluate_distribution(m,epsilon_distribution(p,0))
        r['epsilon_references'][str(eps)]={'behavior_value_start':float(v[m.start]),'greedy_value_start':float(greedy[m.start])}
        np.savez(path/f'epsilon_reference_{eps}.npz',value=v,policy=p,state_ids=m.ids)
    for run in r['runs']:
        d=np.load(path/f'{run["algorithm"]}_{run["exploration"]}_seed{run["seed"]}.npz')
        policy=d['policy'][m.ids]
        for eps in [.1,.02]:
            v=evaluate_distribution(m,epsilon_distribution(policy,eps))
            run['metrics'][f'behavior_value_eps_{eps}']=float(v[m.start])
    summary=[]
    for mode in ['fixed','decay']:
        for alg in ['sarsa','q_learning']:
            group=[x for x in r['runs'] if x['algorithm']==alg and x['exploration']==mode]
            item={'algorithm':alg,'exploration':mode,'n':len(group)}
            for key in ['value_start','start_gap','optimal_actions_fraction','exact_success_500','behavior_value_eps_0.1','behavior_value_eps_0.02','zero_visit_pairs','seconds']:
                values=np.array([x['metrics'][key] for x in group]);item[key+'_mean']=float(values.mean());item[key+'_sd']=float(values.std(ddof=1))
            for key in ['mean_steps','mean_capped_return','success_rate']:
                vals=[x['metrics']['rollout'][key] for x in group];item['rollout_'+key+'_mean']=float(np.mean(vals));item['rollout_'+key+'_sd']=float(np.std(vals,ddof=1))
            summary.append(item)
    r['summary']=summary
    (path/'diagnostics.json').write_text(json.dumps(diagnostics(m,r),indent=2))
    (path/'results.json').write_text(json.dumps(r,indent=2))
    with (path/'summary.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(summary[0]));w.writeheader();w.writerows(summary)
    print(json.dumps({'planning':r['planning'],'epsilon_references':r['epsilon_references'],'summary':summary},indent=2))

if __name__=='__main__':main()
