"""Bounded, explicitly structural ZeroED-local adaptation; never an original ZeroED score."""
import ast,contextlib,hashlib,io,json,os,subprocess,time
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import normalized_mutual_info_score
R=Path(__file__).resolve().parents[1];D=R/'data/sota_followup/zeroed_local';D.mkdir(parents=True,exist_ok=True);O=R/'results/sota_followup/zeroed_local';O.mkdir(parents=True,exist_ok=True)
model=json.loads((R/'evidence/thesis_pilot/local_model_acquisition.json').read_text());weights=R/'data/models'/model['file'];assert hashlib.sha256(weights.read_bytes()).hexdigest()==model['sha256'];calls=[]

def query(tag,instruction):
    prompt='<|im_start|>system\nReturn only the requested JSON. Use unknown when uncertain.<|im_end|>\n<|im_start|>user\n'+instruction+' /no_think<|im_end|>\n<|im_start|>assistant\n<think>\n\n</think>\n';p=D/(tag+'_prompt.txt');p.write_text(prompt);start=time.perf_counter()
    cmd=[str(R/'data/llama_build/bin/llama-completion'),'-m',str(weights),'-f',str(p),'-n','700','-c','2048','--temp','0','--seed','42','-t','2','--no-display-prompt','--grammar-file',str(R/'data/sources/llama.cpp/grammars/json.gbnf')]
    result=subprocess.run(cmd,capture_output=True,text=True,timeout=180);(D/(tag+'_response.txt')).write_text(result.stdout);(D/(tag+'_runtime.log')).write_text(result.stderr)
    text=result.stdout;data=json.loads(text[text.index('{'):text.rfind('}')+1]);calls.append({'stage':tag,'exit_code':result.returncode,'seconds':time.perf_counter()-start,'prompt_sha256':hashlib.sha256(prompt.encode()).hexdigest(),'response_sha256':hashlib.sha256(text.encode()).hexdigest(),'max_new_tokens':700,'threads':2,'temperature':0,'seed':42});assert result.returncode==0;print('Local LLM stage',tag,'completed',flush=True);return data

schema={'amount_cents':{'type':'numeric','nonnegative':True},'status':{'type':'category','values':['BOOKED','PENDING']}}
frame=pd.DataFrame({'amount_cents':[str(100+i) for i in range(160)],'status':['BOOKED' if i%4 else 'PENDING' for i in range(160)]});reference=frame.copy()
for i in [3,19,35,51,67,83,99,115]:frame.at[i,'amount_cents']='INVALID'
for i in [7,23,39,55,71,87,103,119]:frame.at[i,'status']='BROKEN'
truth=(frame!=reference).to_numpy();frame.to_csv(D/'synthetic_dirty.csv',index=False);reference.to_csv(D/'synthetic_reference.csv',index=False)
guidelines=query('guidelines','Synthetic public contract '+json.dumps(schema)+'. Propose at most two candidate checks as JSON {"rules":[{"column":"...","operator":"numeric_nonnegative or enum","values":[]}]}. Unary values must be []; enum values exactly supplied. These are candidate features, not automatically authoritative rules.')
texts=[c+'='+str(frame.at[i,c]) for i in frame.index for c in frame];vectorizer=TfidfVectorizer(analyzer='char',ngram_range=(2,4),max_features=128);X=vectorizer.fit_transform(texts).toarray();labelled={};queries=[];cluster_labels=np.zeros(len(X),int);offset=0
for j,c in enumerate(frame):
    positions=np.array([i*2+j for i in range(len(frame))]);features=X[positions];km=KMeans(n_clusters=6,n_init=10,random_state=42).fit(features);representatives=[]
    for k in range(6):
        members=np.flatnonzero(km.labels_==k)
        if not len(members):continue
        chosen=int(members[np.argmin(np.linalg.norm(features[members]-km.cluster_centers_[k],axis=1))]);rid=int(positions[chosen]);representatives.append({'id':rid,'value':str(frame.iloc[chosen,j])});cluster_labels[positions[members]]=offset+k;queries.append(rid)
    answer=query('labels_'+c,'Contract '+json.dumps(schema[c])+', column '+c+'. Classify the following synthetic dirty values. Return {"labels":[{"id":number,"label":"clean or error or unknown"}]} in the same order: '+json.dumps(representatives))
    mapping={int(v['id']):v['label'] for v in answer.get('labels',[]) if isinstance(v,dict) and v.get('label') in ['clean','error','unknown']}
    for v in representatives:
        if mapping.get(v['id']) in ['clean','error']:labelled[int(cluster_labels[v['id']])]=int(mapping[v['id']]=='error')
    offset+=6
augmentation=query('augmentation','For synthetic contract '+json.dumps(schema)+' generate exactly four extra values, two plausible valid and two invalid. Return {"examples":[{"id":number,"column":"amount_cents or status","value":"string","label":"clean or error"}]}. Do not use any evaluation reference.')
examples=[e for e in augmentation.get('examples',[]) if e.get('column') in schema and e.get('label') in ['clean','error']][:8]
verification=query('verification','Independently re-evaluate these synthetic candidates against contract '+json.dumps(schema)+'. Suggested labels are withheld. Return {"labels":[{"id":number,"label":"clean or error or unknown"}]}: '+json.dumps([{k:e[k] for k in ['id','column','value']} for e in examples]))
review={e['id']:e['label'] for e in verification.get('labels',[]) if isinstance(e,dict)};accepted=[e for e in examples if review.get(e['id'])==e['label']]
train_ids=[i for i in range(len(X)) if int(cluster_labels[i]) in labelled];y=[labelled[int(cluster_labels[i])] for i in train_ids];train=X[train_ids]
if accepted:
    train=np.vstack([train,vectorizer.transform([e['column']+'='+str(e['value']) for e in accepted]).toarray()]);y.extend(int(e['label']=='error') for e in accepted)
status='EXECUTED_STRUCTURAL_ADAPTATION' if len(set(y))==2 else 'BLOCKED_PSEUDOLABEL_SINGLE_CLASS';prediction=np.zeros(len(X),bool);training_log=io.StringIO()
if status.startswith('EXECUTED'):
    tree=ast.parse((R/'data/sources/ZeroED/main.py').read_text());function=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='train_model');ns={'np':np,'MLPClassifier':MLPClassifier};exec(compile(ast.Module(body=[function],type_ignores=[]),'original ZeroED train_model','exec'),ns)
    with contextlib.redirect_stdout(training_log):_,classifier,*_=ns['train_model']('synthetic_cells',train.tolist(),y,60)
    prediction=classifier.predict(X).astype(bool)
hard=np.zeros_like(truth)
hard[:,0]=pd.to_numeric(frame.amount_cents,errors='coerce').isna()|(pd.to_numeric(frame.amount_cents,errors='coerce')<0);hard[:,1]=~frame.status.isin(schema['status']['values']);eligible=np.ones(len(X),bool);eligible[queries]=False;t=truth.ravel();h=hard.ravel()
np.savez_compressed(O/'predictions.npz',prediction=prediction,truth=t,hard=h,eligible=eligible)
summary={'status':status,'model':model,'rows':len(frame),'cells':len(X),'synthetic_contract_errors':int(t.sum()),'representative_queries':len(queries),'pseudo_labelled_clusters':len(labelled),'propagated_training_cells':len(train_ids),'pseudo_label_classes':sorted(set(y)),'augmentation_candidates':len(examples),'augmentation_accepted_after_self_consistency':len(accepted),'same_model_self_consistency_not_external_verification':True,'classifier':'Original released ZeroED train_model function (sklearn MLP), 60 epochs instead of500','guideline_candidates':guidelines,'related_attribute_nmi':float(normalized_mutual_info_score(frame.amount_cents,frame.status)),'R_hits':int((h&t&eligible).sum()),'model_hits':int((prediction&t&eligible).sum()) if status.startswith('EXECUTED') else None,'additional_hits_beyond_R':int((prediction&~h&t&eligible).sum()) if status.startswith('EXECUTED') else None,'model_alerts':int((prediction&eligible).sum()) if status.startswith('EXECUTED') else None,'calls':calls,'source_reference_labels_used_for_training':0,'regime':'U4, only synthetic data; pseudo-labelled transductive pipeline','substantive_stages':['source representation and frequency/related-context qualification','unsupervised clustering and representative selection','local LLM guideline candidates and pseudo-labels','cluster label propagation','LLM augmentation and separate self-consistency check','original released MLP training function','coordinate-aligned prediction and separate reference evaluation'],'deviations':['Qwen3-0.6B replaces original large LLM','character TF-IDF replaces 300-d FastText representation','single-level KMeans replaces original hierarchical feature clustering','candidate JSON rules rather than executing LLM Python functions','synthetic schema-only engineering demonstration, not a published natural-error comparison'],'original_ZeroED_reproduction':False,'scientific_claim':'Architecture feasibility only. No original ZeroED score, semantic gold standard, novel incremental benefit or operational adoption.'}
(D/'classifier_training.log').write_text(training_log.getvalue());(O/'result.json').write_text(json.dumps(summary,indent=2)+'\n');print(json.dumps({k:v for k,v in summary.items() if k not in ['model','guideline_candidates','calls']}),flush=True)
