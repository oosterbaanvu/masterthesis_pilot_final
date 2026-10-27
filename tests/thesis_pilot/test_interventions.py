import pytest
np=pytest.importorskip("numpy", reason="New intervention tests require the separately tested pilot environment")
pd=pytest.importorskip("pandas", reason="New intervention tests require the separately tested pilot environment")
from thesis_pilot.data import load,contracts,SPECS
from thesis_pilot.inject import inject,scenarios
from thesis_pilot.controls import Controls
from thesis_pilot.evaluate import schedule,summarize

@pytest.fixture(scope='module')
def wine():return load('wine')

@pytest.mark.parametrize('mechanism',['ECAR','EAR','ENAR'])
def test_all_changes_replay_and_preserve_original(wine,mechanism):
 parts,_=wine;x=parts['evaluation'][SPECS['wine']['targets']].iloc[:200].copy();before=x.copy()
 for case in scenarios('wine'):
  y,log,diag=inject(x,'wine',case,mechanism,.1,123);z,log2,_=inject(x,'wine',case,mechanism,.1,123)
  assert x.equals(before) and y.equals(z) and log==log2
  actual=(x.astype(str)!=y.astype(str)).to_numpy();assert actual.sum()==len(log)==diag['intended']==diag['realized']
  assert set(e['source_row_id'] for e in log)==set(x.index[actual.any(axis=1)])
  assert all(e['original']!=e['new'] for e in log)

def test_no_zero_scale_injections():
 x=pd.DataFrame({'alcohol':[0.,0.,5.,10.],'density':[1.,2.,3.,4.],'pH':[3.,3.,4.,4.],'sulphates':[1.,1.,1.,1.]},dtype=object)
 y,log,d=inject(x,'wine',scenarios('wine')[2],'ECAR',.5,11)
 assert len(log)==1 and all(float(e['original'])!=0 for e in log)

@pytest.mark.parametrize('name',['credit','bank','wine'])
def test_groups_outcomes_and_baseline_sanity(name):
 parts,meta=load(name);spec=SPECS[name];assert pd.util.hash_pandas_object(parts['history'],index=False).is_unique
 assert all(v==0 for v in meta['group_overlap'].values())
 x=parts['history'][spec['targets']];ev=parts['evaluation'][spec['targets']];cat=[c for c in spec['categorical'] if c in x];c=Controls(contracts(name,parts['history']),spec['targets'],cat).fit(x)
 a,b=c.score(ev);assert a.shape==b.shape==(len(ev),4);assert not a.any();assert np.all(~a|b)
 assert spec['outcome'] not in meta['feature_columns'] and 'ID' not in x
 # Invalid numeric strings must trigger A, rather than silently bypassing range validation.
 bad=ev.copy();target=spec['numeric_target'];bad.iloc[0,bad.columns.get_loc(target)]='BAD'
 aa,_=c.score(bad);assert aa[0,list(bad).index(target)]
 with pytest.raises(ValueError):c.score(ev[list(ev)[::-1]])

def test_already_flagged_is_not_new():
 flags=np.array([[True],[False]]);truth=flags.copy();m=summarize(flags,np.zeros_like(flags),flags,truth,['a','b'],['c'])
 assert m['hits']==1 and m['newly_triggered_hits']==0 and m['already_alerted_changed_cells']==1

def test_total_budget_and_displacement():
 b=[(0,0),(1,0)];d=[(2,0),(3,0)]
 assert schedule(b,d,2,'control_first')==set(b)
 assert schedule(b,d,2,'equal_share')=={(0,0),(2,0)}
 assert len(schedule(b,b,9,'equal_share'))==2

def test_original_mechanism_behavior():
 from tab_err.error_mechanism import ECAR,EAR,ENAR
 n=1000;rng=np.random.default_rng(91);x=pd.DataFrame({'target':rng.permutation(n),'condition':np.arange(n)})
 for cls,column in [(EAR,'condition'),(ENAR,'target')]:
  m=cls(seed=9,**({'condition_to_column':'condition'} if cls==EAR else {})).sample(x,'target',.1)
  ids=m.index[m.target];ranks=x[column].rank().loc[ids];assert len(ids)==100 and ranks.max()-ranks.min()==99
 means=[]
 for seed in range(80):
  m=ECAR(seed=seed).sample(x,'target',.1);means.append(float(x.condition[m.target].mean()/n))
 assert abs(np.mean(means)-.5)<.02

def test_registration_rejects_reference_and_outcome_features(tmp_path):
 import json
 from argparse import Namespace
 from dq_service.__main__ import register
 for forbidden in ['ground_truth','quality','y','is_error','fraud_bool']:
  csv=tmp_path/'source.csv';csv.write_text(forbidden+'\n1\n');contract=tmp_path/'contract.json';contract.write_text(json.dumps({'columns':{forbidden:{'type':'numeric'}},'targets':[forbidden]}))
  with pytest.raises(ValueError,match='Outcome/reference/label'):register(Namespace(csv=str(csv),contract=str(contract),id='leak_test'))


def test_adoption_decision_requires_semantic_and_population_evidence():
 from dq_service.recommend import recommend
 assert recommend({'scope':'generated changes','lower_additional_useful_hits':100})['recommendation']=='INSUFFICIENT_EVIDENCE'
 closed={'scope':'stipulated schema errors only','complete_stipulated_contract_population':True,'baseline_recall':1,'maximum_additional_verified_hits':0}
 assert recommend(closed)['recommendation']=='DO_NOT_ADOPT'
 # Decision-policy fixtures, not actual pilot evidence or an operational certification.
 verified={'reference_kind':'independently_verified_semantic_errors','target_population_match':True,'lower_additional_useful_hits':2,'upper_reviews_per_useful_hit':3,'maximum_acceptable_reviews_per_useful_hit':4}
 assert recommend(verified)['recommendation']=='ADOPT'
 verified['upper_reviews_per_useful_hit']=10
 assert recommend(verified)['recommendation']=='INSUFFICIENT_EVIDENCE'

def test_stable_dboost_population_moments_and_cache_invalidation():
 import runpy,sys
 from pathlib import Path
 root=Path(__file__).resolve().parents[2]
 namespace=runpy.run_path(str(root/'scripts/dboost_stable_compat.py'))
 Stats=namespace['Stats'];s=Stats()
 for _ in range(2400):s.update(.1)
 assert s.sigma==0
 s.update(.2)
 assert abs(s.sigma-np.std(np.array([.1]*2400+[.2])))<1e-14
 assert abs(s.avg-np.mean(np.array([.1]*2400+[.2])))<1e-14
