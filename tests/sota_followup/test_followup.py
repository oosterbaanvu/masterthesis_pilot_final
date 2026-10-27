import hashlib,json,types
from pathlib import Path
import pytest
np=pytest.importorskip('numpy');pd=pytest.importorskip('pandas')
from sota_followup.layers import Layers
from sota_followup.value_metrics import evaluate_values
from sota_followup.interventions import alter
from sota_followup.benchmarks import AutoTestPattern

def test_contextual_layer_detects_in_range_wrong_pair():
    history=pd.DataFrame({'x':np.linspace(0,100,800),'y':2*np.linspace(0,100,800)})
    contract={c:{'type':'numeric','required':True} for c in history};model=Layers(contract,['x','y'],[]).fit(history);flags=model.score_layers(pd.DataFrame({'x':[50.],'y':[150.]}))
    assert not flags['R'].any() and not flags['RS'].any() and flags['RSM'].all()

def test_ambiguous_alerts_consume_capacity_without_becoming_false_negatives():
    flags={'R':[False]*3,'RS':[False]*3,'model':[True,True,False]};rows=evaluate_values(flags,np.array([True,False,False]),np.array([False,True,False]),['a','b','c'],capacities=[1])
    row=next(r for r in rows if r['method']=='model' and r['mode']=='alone' and r['baseline']=='RS')
    assert row['reference_positives']==1 and row['hits']==1 and row['alerts']==2 and row['ambiguous_alerts']==1 and row['reference_nonpositive_alerts']==0

def test_hard_priority_preserves_known_contract_hit_at_fixed_capacity():
    rows=evaluate_values({'R':[True,False],'RS':[True,True],'model':[False,True]},np.array([True,False]),np.zeros(2,bool),['a','b'],capacities=[1],scores={'model':np.array([0.,1.])})
    matched=[r for r in rows if r['method']=='model' and r['mode']=='budget_union'];assert all(r['hits']==1 and r['reviewed']==1 and r['lost_hits']==0 for r in matched)

def test_original_pattern_mapping_retains_duplicate_occurrences_and_column_ids():
    model=AutoTestPattern();model.rules=[(('pattern','synthetic','unused',r'^A\d+$',.5),('pattern',0),.8,.01,[0,1,0,1])]
    flags,_=model.score_columns([{'position':7,'header':'same','values':['A1','A2','bad','bad']},{'position':8,'header':'same','values':['A3','A4']}])
    assert flags[7].tolist()==[False,False,True,True] and not flags[8].any()

def test_wrong_period_noop_population_is_rejected():
    frame=pd.DataFrame({'a':[1.,1.],'b':[1.,1.],'condition':[1.,2.]})
    with pytest.raises(ValueError,match='No non-noop'):alter(frame,('P2','a','period','b'),'ECAR',.5,42,'condition')

def test_timeout_destroys_old_worker_before_reuse(monkeypatch):
    import sota_followup.pattern_adapter as module
    transport=module.BoundedPatternWorker.__new__(module.BoundedPatternWorker);transport.timeout=.01;transport.method='riolu_original';transport.proc=types.SimpleNamespace(stdin=types.SimpleNamespace(write=lambda v:None,flush=lambda:None),stdout=object());events=[]
    monkeypatch.setattr(module.select,'select',lambda *a:([],[],[]));monkeypatch.setattr(transport,'close',lambda:events.append('closed'));monkeypatch.setattr(transport,'start',lambda m:events.append('fresh'))
    result=transport.score(['x','y']);assert events==['closed','fresh'] and result['status']=='BLOCKED_RESOURCE' and result['flags']==[None,None]

def test_wrong_coordinate_arity_fails_closed(monkeypatch):
    import sota_followup.pattern_adapter as module
    transport=module.BoundedPatternWorker.__new__(module.BoundedPatternWorker);transport.timeout=.01;transport.method='riolu_original';stream=types.SimpleNamespace(readline=lambda:'{"ok":true,"result":{"flags":[true]}}\n');transport.proc=types.SimpleNamespace(stdin=types.SimpleNamespace(write=lambda v:None,flush=lambda:None),stdout=stream);events=[]
    monkeypatch.setattr(module.select,'select',lambda *a:([stream],[],[]));monkeypatch.setattr(transport,'close',lambda:events.append('closed'));monkeypatch.setattr(transport,'start',lambda m:events.append('fresh'))
    with pytest.raises(ValueError,match='arity'):transport.score(['x','y'])
    assert events==['closed','fresh']

def test_numeric_pattern_scan_is_inapplicable_without_zero_score(tmp_path,monkeypatch):
    import sota_followup.cli as cli
    (tmp_path/'data/service_registry').mkdir(parents=True);source=tmp_path/'source.csv';source.write_text('value\n1\n2\n');record={'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'contract':{'columns':{'value':{'type':'numeric','required':True}}}};(tmp_path/'data/service_registry/numeric.json').write_text(json.dumps(record));monkeypatch.setattr(cli,'ROOT',tmp_path);monkeypatch.setattr(cli,'BoundedPatternWorker',lambda method:types.SimpleNamespace(close=lambda:None));out=tmp_path/'report';cli.pattern_scan(types.SimpleNamespace(id='numeric',output=str(out),detector='riolu_original'));result=json.loads((out/'report.json').read_text());assert result['eligible_columns']==0 and result['alerts'] is None and result['column_status'][0]['status']=='NOT_APPLICABLE'

def test_changed_source_is_rejected_before_pattern_inference(tmp_path,monkeypatch):
    import sota_followup.cli as cli
    (tmp_path/'data/service_registry').mkdir(parents=True);source=tmp_path/'source.csv';source.write_text('value\nchanged\n');record={'source':str(source),'source_sha256':'0'*64,'contract':{'columns':{}}};(tmp_path/'data/service_registry/changed.json').write_text(json.dumps(record));monkeypatch.setattr(cli,'ROOT',tmp_path)
    with pytest.raises(AssertionError,match='changed'):cli.pattern_scan(types.SimpleNamespace(id='changed',output=str(tmp_path/'out'),detector='riolu_original'))
