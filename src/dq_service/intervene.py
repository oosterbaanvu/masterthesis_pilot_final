"""Generic registered-source interventions and paired evaluation on copies.
No inferred business semantics: only explicit contract failures receive that label.
"""
import hashlib,json,random
from pathlib import Path
import numpy as np
import pandas as pd
from tab_err.error_mechanism import ECAR,EAR,ENAR
from thesis_pilot.controls import Controls
from thesis_pilot.models import ContextualTrees
from thesis_pilot.evaluate import evaluate_all

def experiment(args,root):
 record=json.loads((root/'data/service_registry'/(args.id+'.json')).read_text());source=Path(record['source'])
 if hashlib.sha256(source.read_bytes()).hexdigest()!=record['source_sha256']:raise ValueError('Registered source changed')
 contract=record['contract'];columns=list(contract['columns']);targets=contract.get('targets',columns)
 if args.target not in targets:raise ValueError('Target not in registered scoring contract')
 x=pd.read_csv(source,dtype=str,keep_default_na=False)[columns].astype(object);history=pd.read_csv(args.history,dtype=str,keep_default_na=False)[columns].astype(object)
 x.index=[f'{args.id}:{i}' for i in range(len(x))];spec=contract['columns'][args.target];numeric=spec['type']=='numeric';cat=[c for c in columns if contract['columns'][c]['type']=='category'];values=x[args.target]
 usable=~values.astype(str).isin(['','NULL','None','NaN'])
 if numeric:usable&=pd.to_numeric(values,errors='coerce').notna()
 if args.family=='missing' and not spec.get('required'):raise ValueError('Missing-required experiment needs explicit requiredness')
 if args.family in ['type','scale'] and not numeric:raise ValueError('Operation requires declared numeric source type')
 if args.family=='code':
  if spec['type']!='category' or not spec.get('domain'):raise ValueError('Code operation requires declared domain')
  if args.new_code in spec['domain']:raise ValueError('New code is valid, not a contract violation')
  usable&=values.isin(spec['domain'])
 if args.family=='scale':
  if not np.isfinite(args.factor) or args.factor<=0 or args.factor==1:raise ValueError('Scaling must change nonzero finite values')
  usable&=pd.to_numeric(values,errors='coerce')!=0
 if args.family=='substitution' and values[usable].nunique()<2:raise ValueError('No alternative values for a non-noop substitution')
 eligible=x.loc[usable].copy();n=max(1,int(args.rate*len(eligible)))
 if not 0<args.rate<=1 or not len(eligible):raise ValueError('Invalid rate or empty eligible population')
 for c in eligible:
  if contract['columns'][c]['type']=='numeric':eligible[c]=pd.to_numeric(eligible[c],errors='coerce')
 if args.mechanism=='EAR' and (args.condition not in columns or args.condition==args.target):raise ValueError('EAR requires a different permitted source conditioning field')
 kwargs={'seed':args.seed}
 if args.mechanism=='EAR':kwargs['condition_to_column']=args.condition
 state=random.getstate()
 try:mask={'ECAR':ECAR,'EAR':EAR,'ENAR':ENAR}[args.mechanism](**kwargs).sample(eligible,args.target,(n+.1)/len(eligible) if n<len(eligible) else 1.)
 finally:random.setstate(state)
 ids=mask.index[mask[args.target]];changed=x.copy();logs=[];rng=np.random.default_rng(args.seed)
 for rowid in ids:
  before=values.loc[rowid]
  if args.family=='missing':after=''
  elif args.family=='type':after='INVALID_NUMERIC'
  elif args.family=='code':after=args.new_code
  elif args.family=='scale':after=str(float(before)*args.factor)
  else:
   pool=values[usable & (values.astype(str)!=str(before))]
   if numeric:pool=pool[pd.to_numeric(pool)!=float(before)]
   if pool.empty:raise ValueError('No non-equivalent donor')
   after=str(pool.iloc[rng.integers(len(pool))])
  if str(after)==str(before):raise ValueError('No-op intervention')
  changed.at[rowid,args.target]=after;logs.append({'row_id':rowid,'column':args.target,'original':str(before),'new':str(after)})
 delta=(changed.astype(str)!=x.astype(str)).to_numpy();assert delta.sum()==len(ids)==n
 label='VERIFIED_STIPULATED_CONTRACT_VIOLATION' if args.family in ['missing','type','code'] else 'CONTROLLED_ALTERATION'
 rules=Controls(contract['columns'],targets,cat).fit(history);model=ContextualTrees().fit(history,targets,cat)
 originals={};originals['A'],originals['B']=rules.score(x);originals[model.name]=model.score(x)
 preds={};preds['A'],preds['B']=rules.score(changed);preds[model.name]=model.score(changed)
 truth=np.zeros((len(x),len(targets)),bool)
 for rowid in ids:truth[x.index.get_loc(rowid),targets.index(args.target)]=True
 meta={'scenario':args.id+'_registered_intervention','dataset':args.id,'family':args.family,'mechanism':args.mechanism,'rate':args.rate,'seed':args.seed,'target':args.target,'label_status':label}
 metrics=evaluate_all(preds,originals,truth,list(x.index),targets,meta);out=Path(args.output);out.mkdir(parents=True,exist_ok=True)
 changed.to_csv(out/'dirty_copy.csv',index_label='source_row_id');(out/'injection_values.json').write_text(json.dumps(logs,indent=2));np.savez_compressed(out/'predictions.npz',truth=truth,**preds)
 result={'state':'EXECUTED_CONDITIONAL','registered_source':args.id,'source_sha256':record['source_sha256'],'original_source_unchanged':hashlib.sha256(source.read_bytes()).hexdigest()==record['source_sha256'],'rows':len(x),'unit':'cell','eligible_count':len(eligible),'intended_changes':n,'realized_changes':int(truth.sum()),'label_status':label,'detector_abstained_invalid_numeric_targets':int(sum(pd.to_numeric(changed[c],errors='coerce').isna().sum() for c in targets if contract['columns'][c]['type']=='numeric')),'recommendation':'INSUFFICIENT_EVIDENCE','limitations':'Known injected contract failures or alteration recovery only; off-change source correctness unknown. No operational adoption from synthetic performance.','metrics':metrics}
 (out/'report.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='metrics'}));return result
