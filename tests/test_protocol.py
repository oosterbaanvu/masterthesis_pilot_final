import pytest
from thesis_audit.protocol import DirtyTable, evaluate, compatibility, run_rules, budget_review
from thesis_audit.audit import classify, parse_list, read_table, equivalent_number
from thesis_audit.acquire import acquire_one

def test_no_fabricated_marginal_precision():
    assert evaluate(range(3),{0},set(),{0},{0})['marginal_precision'] is None

def test_uncertain_reviews_still_consume_budget():
    r=evaluate(range(4),{0},{1},{0},{1,2})
    assert r['additional_alerts']==2 and r['additional_unscored']==1 and r['marginal_precision']==0
    assert budget_review([1,0],1,range(4))=={1}

@pytest.mark.parametrize('col',['ground_truth','reference','label','is_error','fraud_bool','y','class'])
def test_deliberate_label_leak_is_rejected(col):
    with pytest.raises(ValueError):DirtyTable((col,),(('1',),)).validate([col])

def test_disguised_reference_role_is_rejected():
    with pytest.raises(ValueError):DirtyTable(('amount',),(('1',),),role='clean_reference').validate(['amount'])

def test_unapproved_feature_and_ragged_rejected():
    with pytest.raises(ValueError):DirtyTable(('amount','secret'),()).validate(['amount'])
    with pytest.raises(ValueError):DirtyTable(('amount',),((),)).validate(['amount'])

@pytest.mark.parametrize('method,level',[('cdc','column_value'),('dboost','column_value'),('isolation_forest','cell'),('autotest_sdc','row'),('raha','cell')])
def test_incompatible_target_rejected(method,level):
    assert compatibility(method,level)=='INCOMPATIBLE'

def test_explicit_conditional_information():
    assert compatibility('cdc','cell',clean_history=True)=='CONDITIONAL'
    assert compatibility('raha','cell',labelled_reference=True)=='CONDITIONAL'

def test_rules_schema_numeric_guards_and_missing():
    t=DirtyTable(('amount','code'),(('NaN','A'),('10','BAD'),('?','A'),('5','A')))
    rules={'amount':{'missing_tokens':['?'],'numeric':True,'bounds':[0,100]},'code':{'permitted_values':['A']}}
    assert run_rules(t,t.columns,rules)=={(0,0),(1,1),(2,0)}

def test_identifiers_not_normalized():
    assert classify('raha_tax','zip','01907','1907')[0]=='DEBATABLE_OR_UNCERTAIN'
    assert classify('cars','Weight','3504.','3504.0')[0]=='REPRESENTATION_ONLY'
    assert not equivalent_number('NaN','NaN')

@pytest.mark.parametrize('text',['',"['refridgerator'+C1187]","__import__('os').system('false')","{'a':1}","[1]"])
def test_unsafe_or_unknown_annotations_rejected(text):
    with pytest.raises(ValueError):parse_list(text)

def test_units_do_not_become_semantic_errors():
    assert classify('raha_beers','abv','0.09%','0.09')[0]=='DEBATABLE_OR_UNCERTAIN'
    assert classify('raha_hospital','city','birminghxm','birmingham')[0]!='VERIFIED_REFERENCE_ERROR'

def test_hash_mismatch_is_not_overwritten(tmp_path):
    p=tmp_path/'raw';p.write_text('bad')
    with pytest.raises(ValueError):acquire_one({'path':'raw','bytes':3,'sha256':'bad','url':'https://invalid.example/'},tmp_path)
    assert p.read_text()=='bad'

def test_shift_schema_guard(tmp_path):
    p=tmp_path/'bad.csv';p.write_text('id,value\n1,2,3\n')
    with pytest.raises(ValueError):read_table(p)

def test_invalid_metric_populations():
    with pytest.raises(ValueError):evaluate({0},{0},{0},{0},set())
    with pytest.raises(ValueError):evaluate({0},{0},set(),{1},set())

def test_generated_deletion_is_not_automatically_contract_violation():
    assert classify('cars','Horsepower','?','130')[0]=='DEBATABLE_OR_UNCERTAIN'
    assert classify('restaurant','class','?','0')[0]=='DEBATABLE_OR_UNCERTAIN'
