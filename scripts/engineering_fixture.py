"""Explicit synthetic linked-table control demonstration. No real financial evidence."""
import copy,json,hashlib,subprocess,os,sys
from pathlib import Path
import pandas as pd
from thesis_pilot.data import ROOT
r=ROOT/'data/engineering_fixture';r.mkdir(exist_ok=True)
accounts=pd.DataFrame([{'account_id':f'A{i:03d}','status':'OPEN'} for i in range(40)])
transactions=pd.DataFrame([{'transaction_id':f'T{i:04d}','account_id':f'A{i%40:03d}','amount_cents':100+i,'status':'BOOKED','delivery':'D1'} for i in range(200)])
ledger=pd.DataFrame([{'entry_id':f'L{i:04d}{side}','transaction_id':f'T{i:04d}','side':side,'amount_cents':100+i} for i in range(200) for side in ['DEBIT','CREDIT']])
original={'accounts':accounts,'transactions':transactions,'ledger':ledger}

def check(tables,extended):
 f=[]
 for name,df in tables.items():
  key={'accounts':'account_id','transactions':'transaction_id','ledger':'entry_id'}[name]
  if df[key].duplicated().any():f.append((name,'UNIQUE_KEY'))
  if df.isna().any().any() or (df.astype(str)=='').any().any():f.append((name,'REQUIRED'))
  if 'amount_cents' in df:
   val=pd.to_numeric(df.amount_cents,errors='coerce')
   if val.isna().any() or (val%1!=0).any() or (val<0).any():f.append((name,'INTEGER_NONNEGATIVE_CENTS'))
  if name=='transactions' and not df.status.isin(['BOOKED','PENDING']).all():f.append((name,'STATUS_DOMAIN'))
 if extended:
  a,tx,le=tables['accounts'],tables['transactions'],tables['ledger']
  if not tx.account_id.isin(a.account_id).all():f.append(('transactions','ACCOUNT_FOREIGN_KEY'))
  if not le.transaction_id.isin(tx.transaction_id).all():f.append(('ledger','TRANSACTION_FOREIGN_KEY'))
  if len(tx)!=200:f.append(('transactions','EXPECTED_DELIVERY_COUNT'))
  debit=le.loc[le.side=='DEBIT'].groupby('transaction_id').amount_cents.sum();credit=le.loc[le.side=='CREDIT'].groupby('transaction_id').amount_cents.sum()
  if not debit.equals(credit):f.append(('ledger','DEBIT_CREDIT_RECONCILIATION'))
  amounts=tx.set_index('transaction_id').amount_cents
  if not debit.reindex(amounts.index).equals(amounts):f.append(('ledger','SOURCE_LEDGER_RECONCILIATION'))
 return sorted(set(f))
assert check(original,False)==check(original,True)==[]
cases=[]
for name in ['foreign_key','duplicate_key','unsupported_status','missing_delivery','ledger_imbalance','source_aggregate_mismatch','required_missing','invalid_numeric']:
 x={k:v.copy(deep=True) for k,v in original.items()}
 if name=='foreign_key':x['transactions'].loc[0,'account_id']='NO_SUCH_ACCOUNT'
 elif name=='duplicate_key':x['transactions'].loc[1,'transaction_id']=x['transactions'].loc[0,'transaction_id']
 elif name=='unsupported_status':x['transactions'].loc[0,'status']='INVALID'
 elif name=='missing_delivery':x['transactions']=x['transactions'].iloc[:-1].copy()
 elif name=='ledger_imbalance':x['ledger'].loc[0,'amount_cents']+=1
 elif name=='source_aggregate_mismatch':x['transactions'].loc[0,'amount_cents']+=1
 elif name=='required_missing':x['transactions'].loc[0,'status']=''
 elif name=='invalid_numeric':x['transactions']['amount_cents']=x['transactions'].amount_cents.astype(object);x['transactions'].loc[0,'amount_cents']='BAD'
 a,b=check(x,False),check(x,True);assert b;cases.append({'scenario':name,'basic_findings':a,'extended_findings':b,'label':'EXPLICIT_STIPULATED_CONTRACT','unit':'table/rule event; not cell detection leaderboard'})
for name,df in original.items():df.to_csv(r/(name+'.csv'),index=False)
# Actual CLI demonstration on registered transactions, excluding identifiers from scored features.
columns={'amount_cents':{'type':'numeric','required':True,'bounds':[0,None],'provenance':'EXPLICIT_STIPULATED_CONTRACT'},'status':{'type':'category','required':True,'domain':['BOOKED','PENDING'],'provenance':'EXPLICIT_STIPULATED_CONTRACT'}}
contract={'columns':columns,'targets':list(columns),'excluded_columns':['transaction_id','account_id','delivery']};(r/'contract.json').write_text(json.dumps(contract,indent=2))
new=transactions.copy();new['amount_cents']=new.amount_cents.astype(object);new.loc[0,'amount_cents']='BAD';new.loc[1,'status']='INVALID';new.to_csv(r/'new_delivery.csv',index=False)
env=dict(os.environ,PYTHONPATH=str(ROOT/'src'));py=str(ROOT/'data/envs/pilot/bin/python')
commands=[[py,'-m','dq_service','register','--id','synthetic_finance_demo','--csv',str(r/'new_delivery.csv'),'--contract',str(r/'contract.json')],[py,'-m','dq_service','scan','--id','synthetic_finance_demo','--history',str(r/'transactions.csv'),'--output',str(ROOT/'results/thesis_pilot/service_demo')]]
logs=[]
for cmd in commands:
 p=subprocess.run(cmd,env=env,cwd=ROOT,capture_output=True,text=True);logs.append({'command':cmd,'exit_code':p.returncode,'stdout':p.stdout,'stderr':p.stderr});assert p.returncode==0,logs[-1]
out={'state':'EXECUTED_VALID','synthetic_only':True,'untouched_findings':[],'scenarios':cases,'cli_executions':logs,'control_provenance':'All fixture invariants explicitly stipulated independently of mutations; no claim these are bank production rules.'}
(ROOT/'results/thesis_pilot/engineering_fixture.json').write_text(json.dumps(out,indent=2));print('8 linked-table intervention cases validated; register and scan CLI executed.')
