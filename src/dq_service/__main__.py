import argparse,hashlib,json,sys,re
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]

def register(args):
 import pandas as pd
 if not re.fullmatch(r'[A-Za-z0-9_.-]+',args.id):raise ValueError('Invalid source identifier')
 source=Path(args.csv).resolve();contract=json.loads(Path(args.contract).read_text());df=pd.read_csv(source,dtype=str,keep_default_na=False)
 excluded=contract.get('excluded_columns',[]);cols=contract['columns'];targets=contract.get('targets',list(cols))
 forbidden={'ground_truth','is_error','label','reference_value','clean_value','y','quality','fraud_bool','default payment next month'}
 if set(cols)&forbidden:raise ValueError('Outcome/reference/label columns cannot be registered as detector features')
 if not set(cols)<=set(df) or set(cols)&set(excluded):raise ValueError('Invalid contract feature or outcome columns')
 if not set(targets)<=set(cols):raise ValueError('Invalid target population')
 reg=ROOT/'data/service_registry';reg.mkdir(exist_ok=True)
 record={'id':args.id,'source':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'contract':contract,'rows':len(df),'columns':list(df),'not_a_data_error_label':excluded}
 (reg/(args.id+'.json')).write_text(json.dumps(record,indent=2));print(json.dumps({'registered':args.id,'rows':len(df),'sha256':record['source_sha256']}))

def scan(args):
 import pandas as pd
 import numpy as np
 from thesis_pilot.controls import Controls
 from thesis_pilot.models import ContextualTrees
 record=json.loads((ROOT/'data/service_registry'/(args.id+'.json')).read_text());contract=record['contract'];source=Path(record['source'])
 if hashlib.sha256(source.read_bytes()).hexdigest()!=record['source_sha256']:raise ValueError('Registered source changed')
 cols=list(contract['columns']);targets=contract.get('targets',cols);cat=[c for c in cols if contract['columns'][c]['type']=='category']
 batch=pd.read_csv(source,dtype=str,keep_default_na=False)[cols].astype(object);history=pd.read_csv(args.history,dtype=str,keep_default_na=False)[cols].astype(object)
 rules=Controls(contract['columns'],targets,cat).fit(history);a,b=rules.score(batch);preds={'basic_controls':a,'extended_controls':b}
 detector_status='NOT_EXECUTED'
 if args.detector!='none':
  model=None
  try:
   if args.detector=='contextual_extra_trees':
    model=ContextualTrees().fit(history,targets,cat)
   else:
    from thesis_pilot.models import Native
    source_map={'dboost_text_original':(ROOT/'data/sources/cpitclaudel__dBoost',ROOT/'data/envs/pilot/bin/python'),'lucario_original_history':(ROOT/'data/sources/mooselab__Detect-Cell-level-Data-Anomalies-With-LUCARIO',ROOT/'data/envs/lucario/bin/python'),'cdc_original':(Path('/workspace/research_sources/se-jaeger__conformal-data-cleaning'),ROOT/'data/envs/cdc/bin/python')}
    source,python=source_map[args.detector];model=Native(args.detector,source,python).fit(history,targets,cat,'service_'+args.id)
   preds[args.detector]=model.score(batch);detector_status='EXECUTED_CONDITIONAL'
  except Exception as error:detector_status='BLOCKED_TECHNICAL: '+repr(error)
  finally:
   if model:model.close()
 findings=[]
 for method,flags in preds.items():
  for i,j in zip(*np.where(flags)):findings.append({'row_position':int(i),'column':targets[j],'method':method,'interpretation':'contract violation' if method=='basic_controls' else 'statistical suspicion; not verified semantic error'})
 out=Path(args.output);out.mkdir(parents=True,exist_ok=True);pd.DataFrame(findings,columns=['row_position','column','method','interpretation']).to_csv(out/'findings.csv',index=False)
 result={'dataset':args.id,'rows':len(batch),'scored_columns':targets,'counts':{m:int(f.sum()) for m,f in preds.items()},'recommendation':'INSUFFICIENT_EVIDENCE','reason':'Operational source scan has no independent error labels; suspicion alone cannot justify adoption. Consult qualified pilot evidence and domain review.','reference_scope':'history provided separately; source values never treated as confirmed clean','detector':args.detector,'detector_status':detector_status}
 (out/'report.json').write_text(json.dumps(result,indent=2));print(json.dumps(result))

def main():
 parser=argparse.ArgumentParser(prog='dqeval');sub=parser.add_subparsers(dest='command',required=True)
 p=sub.add_parser('register');p.add_argument('--id',required=True);p.add_argument('--csv',required=True);p.add_argument('--contract',required=True);p.set_defaults(func=register)
 p=sub.add_parser('scan');p.add_argument('--id',required=True);p.add_argument('--history',required=True);p.add_argument('--output',required=True);p.add_argument('--detector',choices=['none','contextual_extra_trees','dboost_text_original','lucario_original_history','cdc_original'],default='contextual_extra_trees');p.set_defaults(func=scan)
 p=sub.add_parser('experiment');p.add_argument('--id',required=True);p.add_argument('--history',required=True);p.add_argument('--output',required=True);p.add_argument('--target',required=True);p.add_argument('--family',choices=['missing','type','code','scale','substitution'],required=True);p.add_argument('--mechanism',choices=['ECAR','EAR','ENAR'],default='ECAR');p.add_argument('--condition');p.add_argument('--rate',type=float,default=.05);p.add_argument('--seed',type=int,default=42);p.add_argument('--factor',type=float,default=10);p.add_argument('--new-code',default='__INVALID_CODE__')
 p=sub.add_parser('pilot');p.add_argument('--datasets',nargs='+',default=['credit','bank','wine']);p.add_argument('--smoke',action='store_true')
 args=parser.parse_args()
 if args.command=='experiment':
  from .intervene import experiment
  experiment(args,ROOT)
 elif args.command=='pilot':
  from thesis_pilot.run import run_dataset
  for name in args.datasets:run_dataset(name,args.smoke)
 else:args.func(args)
if __name__=='__main__':main()
