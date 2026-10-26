import hashlib,io,json,zipfile
from pathlib import Path
import numpy as np
import pandas as pd
import xlrd
ROOT=Path(__file__).resolve().parents[2]
SPECS={
'credit':{'targets':['AGE','LIMIT_BAL','BILL_AMT1','EDUCATION'],'condition':'LIMIT_BAL','amount':'BILL_AMT1','numeric_target':'AGE','category':'EDUCATION','categorical':['SEX','EDUCATION','MARRIAGE','PAY_0','PAY_2','PAY_3','PAY_4','PAY_5','PAY_6'],'outcome':'default payment next month'},
'bank':{'targets':['age','duration','previous','job'],'condition':'age','amount':'duration','numeric_target':'previous','category':'job','categorical':['job','marital','education','default','housing','loan','contact','month','day_of_week','poutcome'],'outcome':'y'},
'wine':{'targets':['alcohol','density','pH','sulphates'],'condition':'density','amount':'alcohol','numeric_target':'pH','category':None,'categorical':[],'outcome':'quality'}}

def shash(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def load(name):
 if name=='credit':
  p=ROOT/'data/recovery_downloads/default+of+credit+card+clients.zip'
  with zipfile.ZipFile(p) as z:
   s=xlrd.open_workbook(file_contents=z.read(next(x for x in z.namelist() if x.endswith('.xls')))).sheet_by_index(0)
   h=[str(x) for x in s.row_values(1)]; rows=[s.row_values(i) for i in range(2,s.nrows)]; df=pd.DataFrame(rows,columns=h)
  outcome=df.columns[-1];df=df.drop(columns=['ID',outcome])
 elif name=='bank':
  p=ROOT/'data/recovery_downloads/bank+marketing.zip'
  with zipfile.ZipFile(p) as z:
   with zipfile.ZipFile(io.BytesIO(z.read('bank-additional.zip'))) as zz:
    b=zz.read('bank-additional/bank-additional-full.csv');df=pd.read_csv(io.BytesIO(b),sep=';').drop(columns=['y'])
 else:
  p=ROOT/'data/pilot_sources/wine.zip'
  with zipfile.ZipFile(p) as z:df=pd.read_csv(io.BytesIO(z.read('winequality-white.csv')),sep=';').drop(columns=['quality'])
 expected_files=json.loads((ROOT/'manifests/files.json').read_text());expected={x['path']:x['sha256'] for x in expected_files}
 if name=='wine':expected[str(p.relative_to(ROOT))]='3ed56667f4b828242bd732d7d1dd7f2861e54432239d7fa63877014cbb0304d4'
 if shash(p)!=expected[str(p.relative_to(ROOT))]:raise ValueError('Source hash mismatch')
 for c in df:
  if c in SPECS[name]['categorical']:
   df[c]=df[c].map(lambda x:str(int(x)) if isinstance(x,(int,float)) and float(x).is_integer() else str(x))
  else:df[c]=pd.to_numeric(df[c],errors='raise').astype(float)
 df.index=pd.Index([f'{name}:{i}' for i in range(len(df))],name='source_row_id')
 df=df.astype(object)
 # Outcome-free exact feature groups determine disjoint partitions; original data not assumed clean.
 keys=pd.util.hash_pandas_object(df,index=False).astype(str)
 groups=keys.map(lambda x:int(hashlib.sha256(('thesis-pilot-v1|'+x).encode()).hexdigest()[:12],16)/16**12)
 partitions={}
 for label,lo,hi,cap in [('history',0,.5,2400),('development',.5,.6,400),('evaluation',.6,.8,800),('reserved',.8,1,None)]:
  ids=df.index[(groups>=lo)&(groups<hi)].tolist();ids=sorted(ids,key=lambda x:hashlib.sha256(x.encode()).hexdigest())
  if cap:ids=ids[:cap]
  partitions[label]=df.loc[ids].copy()
 meta={'dataset':name,'source_sha256':shash(p),'full_rows':len(df),'feature_columns':list(df),'evaluated_targets':SPECS[name]['targets'],'outcome_excluded':True,'parts':{k:list(v.index) for k,v in partitions.items()},'group_overlap':{}}
 for a,b in [('history','evaluation'),('development','evaluation'),('history','reserved')]:
  overlap=set(keys.loc[partitions[a].index])&set(keys.loc[partitions[b].index]);assert not overlap;meta['group_overlap'][a+'_'+b]=len(overlap)
 return partitions,meta

def contracts(name,history):
 spec=SPECS[name];contracts={}
 for c in history:
  cat=c in spec['categorical']
  x={'required':True,'type':'category' if cat else 'numeric','provenance':'EXPLICIT_STIPULATED_CONTRACT','evidence':'Operational feed: every declared feature supplied, numeric lexical validity; stipulation is not an assertion that publisher demands completeness.'}
  if cat:
   if name=='credit':
    domain={'SEX':['1','2'],'EDUCATION':list(map(str,range(7))),'MARRIAGE':list(map(str,range(4)))}
    x['domain']=domain.get(c,list(map(str,range(-2,10))));x['evidence']+=' Permissive codes include known legitimate/uncertain source exceptions; no claim those exceptions are errors.'
   else:
    domains={'job':['admin.','blue-collar','entrepreneur','housemaid','management','retired','self-employed','services','student','technician','unemployed','unknown'],'marital':['divorced','married','single','unknown'],'education':['basic.4y','basic.6y','basic.9y','high.school','illiterate','professional.course','university.degree','unknown'],'default':['no','yes','unknown'],'housing':['no','yes','unknown'],'loan':['no','yes','unknown'],'contact':['cellular','telephone'],'month':['jan','feb','mar','apr','may','jun','jul','aug','sep','oct','nov','dec'],'day_of_week':['mon','tue','wed','thu','fri'],'poutcome':['failure','nonexistent','success']}
    x['domain']=domains[c];x['provenance']='DOCUMENTED_SOURCE_CONTRACT';x['evidence']='bank-additional-names.txt category list; unknown is retained as a legitimate source token. Requiredness separately stipulated.'
  elif name=='wine':
   x['bounds']=[0,14] if c=='pH' else ([0,100] if c=='alcohol' else [0,None]);x['bounds_provenance']='EXPLICIT_STIPULATED_CONTRACT';x['bounds_evidence']='Physical measurement units: concentrations/density nonnegative, pH aqueous operational interval 0..14 and alcohol percentage 0..100 (explicit operational convention).'
  elif c in ['AGE','age','duration','previous','campaign','pdays']:
   x['bounds']=[0,None];x['bounds_provenance']='EXPLICIT_STIPULATED_CONTRACT';x['bounds_evidence']='Nonnegative count/age/duration convention; no arbitrary upper bound.'
  contracts[c]=x
 return contracts
