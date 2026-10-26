import hashlib
import numpy as np

def ordering(flags,rowids,targets):
 coords=list(zip(*np.where(flags)))
 return sorted(coords,key=lambda ij:hashlib.sha256((str(rowids[ij[0]])+'|'+targets[ij[1]]).encode()).digest())

def schedule(base,det,k,policy):
 b=list(base);d=list(det)
 if policy=='control_first':seq=b+d
 else:
  seq=[]
  # Round robin reserves equal opportunities without inventing confidence scores.
  for i in range(max(len(b),len(d))):
   if i<len(b):seq.append(b[i])
   if i<len(d):seq.append(d[i])
 out=[];seen=set()
 for ij in seq:
  if ij not in seen:out.append(ij);seen.add(ij)
  if len(out)>=k:break
 return set(out)

def summarize(flags,base,untouched,truth,rows,targets):
 f=set(zip(*np.where(flags)));b=set(zip(*np.where(base)));u=set(zip(*np.where(untouched)));t=set(zip(*np.where(truth)))
 hit=f&t;extra=f-b;new=f-u
 return {'hits':len(hit),'changed_cells':len(t),'change_recall':len(hit)/len(t) if t else None,'alerts':len(f),'off_change_alerts_unknown':len(f-t),'reference_precision':len(hit)/len(f) if f else None,'f1_reference':2*len(hit)/(len(f)+len(t)) if len(f)+len(t) else None,'additional_hits':len(extra&t),'additional_alerts':len(extra),'marginal_reference_precision':len(extra&t)/len(extra) if extra else None,'newly_triggered_hits':len(new&t),'already_alerted_changed_cells':len(u&t),'newly_triggered_alerts':len(new)}

def evaluate_all(preds,original,truth,rowids,targets,meta):
 records=[]
 for baseline in ['A','B']:
  base=preds[baseline];orig=original[baseline];bo=ordering(base,rowids,targets)
  for method in preds:
   if method in ['A','B'] and method!=baseline:continue
   flag=preds[method];untouched=original[method]
   combos=[('alone',flag,untouched)] if method==baseline else [('alone',flag,untouched),('union',base|flag,orig|untouched)]
   for mode,f,u in combos:
    rec=dict(meta,baseline=baseline,method=method,mode=mode,budget_per_1000=None,policy='unconstrained');rec.update(summarize(f,base,u,truth,rowids,targets));records.append(rec)
   do=ordering(flag,rowids,targets)
   for budget in [10,25,50]:
    k=max(1,int(np.ceil(budget*len(rowids)/1000)))
    for policy in ['control_first','equal_share']:
     selected=schedule(bo,do,k,policy);base_selected=set(bo[:k]);t=set(zip(*np.where(truth)))
     rec=dict(meta,baseline=baseline,method=method,mode='budget_union',budget_per_1000=budget,policy=policy,capacity=k,reviewed=len(selected),hits=len(selected&t),baseline_budget_hits=len(base_selected&t),additional_hits=len((selected-base_selected)&t),lost_baseline_hits=len((base_selected-selected)&t),net_hits=len(selected&t)-len(base_selected&t),changed_cells=len(t),change_recall=len(selected&t)/len(t) if t else None,alerts=len(selected),off_change_alerts_unknown=len(selected-t))
     records.append(rec)
 return records
