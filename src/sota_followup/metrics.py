import hashlib
import itertools
import numpy as np

def coordinates(flags):
    return set(map(tuple, np.argwhere(flags)))

def ordered(flags, ids, columns):
    return sorted(coordinates(flags), key=lambda ij: hashlib.sha256(f'{ids[ij[0]]}|{columns[ij[1]]}'.encode()).digest())

def select(hard, baseline, detector, k, policy):
    hard = list(hard)
    h = set(hard)
    b = [v for v in baseline if v not in h]
    d = [v for v in detector if v not in h]
    tail = b+d if policy == 'control_first' else [v for pair in itertools.zip_longest(b,d) for v in pair if v is not None]
    return set(list(dict.fromkeys(hard+tail))[:k])

def evaluate(predictions, untouched, truth, ids, columns, budgets=(10,25,50)):
    t = coordinates(truth)
    rows = []
    for baseline in ['R','RS','RSM']:
        b = coordinates(predictions[baseline])
        for method, flag in predictions.items():
            d = coordinates(flag)
            u = coordinates(untouched[method])
            for mode, f in [('alone',d),('union',b|d)]:
                rows.append({'baseline':baseline,'method':method,'mode':mode,'policy':'unconstrained','budget':None,'hits':len(f&t),'alerts':len(f),'positives':len(t),'extra_hits':len((f-b)&t),'extra_alerts':len(f-b),'new_detector_hits':len((d-u)&t),'off_reference_alerts_unknown':len(f-t)})
            for budget in budgets:
                k=max(1,int(np.ceil(len(ids)*budget/1000)))
                for policy in ['control_first','equal_share']:
                    hard=ordered(predictions['R'],ids,columns)
                    bo=ordered(predictions[baseline],ids,columns)
                    selected=select(hard,bo,ordered(flag,ids,columns),k,policy)
                    bs=select(hard,bo,[],k,policy)
                    rows.append({'baseline':baseline,'method':method,'mode':'budget_union','policy':policy,'budget':budget,'capacity':k,'reviewed':len(selected),'hits':len(selected&t),'positives':len(t),'extra_hits':len((selected-bs)&t),'lost_hits':len((bs-selected)&t),'net_hits':len(selected&t)-len(bs&t),'alerts':len(selected),'off_reference_alerts_unknown':len(selected-t)})
    return rows
