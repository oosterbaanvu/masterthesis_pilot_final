"""Common value-unit costs; no relational context or invented occurrence frequencies."""
import hashlib,itertools
import numpy as np

def evaluate_values(flags,truth,ambiguous,identities,capacities=(25,50,100),scores=None):
    t=set(np.flatnonzero(truth));amb=set(np.flatnonzero(ambiguous));n=len(identities);rows=[]
    def order(f,score=None):
        return sorted(np.flatnonzero(f),key=lambda i:((-float(score[i])) if score is not None else 0,hashlib.sha256(str(identities[i]).encode()).digest()))
    for method,raw in flags.items():
        applicable=np.asarray([v is not None and not (isinstance(v,float) and np.isnan(v)) for v in raw]);universe=set(np.flatnonzero(applicable));d=np.asarray([bool(v) if ok else False for v,ok in zip(raw,applicable)],bool)
        for baseline in ['R','RS']:
            b=np.asarray(flags[baseline],bool)&applicable;h=np.asarray(flags['R'],bool)&applicable;bs=set(np.flatnonzero(b));ds=set(np.flatnonzero(d));known=universe-amb;target=t&known
            for mode,s in [('alone',ds),('union',bs|ds)]:
                rows.append({'baseline':baseline,'method':method,'mode':mode,'policy':'unconstrained','capacity':None,'eligible_values':len(universe),'reference_positives':len(target),'hits':len(s&target),'alerts':len(s),'ambiguous_alerts':len(s&amb),'reference_nonpositive_alerts':len((s&known)-target),'extra_hits':len((s-bs)&target),'extra_alerts':len(s-bs)})
            policies=['control_first','equal_share']+(['native_ranked_equal_share'] if scores is not None and method in scores else [])
            for k in capacities:
                for policy in policies:
                    hard=order(h);hs=set(hard);bo=[i for i in order(b) if i not in hs];do=[i for i in order(d,scores[method] if policy=='native_ranked_equal_share' else None) if i not in hs]
                    seq=bo+do if policy=='control_first' else [v for pair in itertools.zip_longest(bo,do) for v in pair if v is not None]
                    s=set(list(dict.fromkeys(hard+seq))[:k]);base_selected=set((hard+bo)[:k])
                    rows.append({'baseline':baseline,'method':method,'mode':'budget_union','policy':policy,'capacity':k,'eligible_values':len(universe),'reference_positives':len(target),'reviewed':len(s),'hits':len(s&target),'alerts':len(s),'ambiguous_alerts':len(s&amb),'extra_hits':len((s-base_selected)&target),'lost_hits':len((base_selected-s)&target),'net_hits':len(s&target)-len(base_selected&target)})
    return rows
