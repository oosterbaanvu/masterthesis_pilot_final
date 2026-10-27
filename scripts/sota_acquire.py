"""Fetch only pinned public follow-up dependencies; never overwrite changed artifacts."""
import argparse,hashlib,json,subprocess,urllib.request
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for block in iter(lambda:f.read(8*1024*1024),b''):h.update(block)
 return h.hexdigest()
def fetch(item,path):
 path.parent.mkdir(parents=True,exist_ok=True)
 if not path.exists():
  tmp=path.with_name(path.name+'.part')
  if 'url' in item:
   with urllib.request.urlopen(item['url'],timeout=120) as source,tmp.open('wb') as dest:
    import shutil;shutil.copyfileobj(source,dest)
  else:
   import gdown
   result=gdown.download(id=item['id'],output=str(tmp),quiet=False,use_cookies=False)
   if result is None:raise RuntimeError('Author public download unavailable: '+item['id'])
  if digest(tmp)!=item['sha256'] or tmp.stat().st_size!=item['bytes']:raise ValueError('Downloaded artifact identity mismatch: '+str(path))
  tmp.rename(path)
 if digest(path)!=item['sha256'] or path.stat().st_size!=item['bytes']:raise ValueError('Existing artifact identity mismatch: '+str(path))
 print('verified',path.relative_to(R),flush=True)
def main():
 p=argparse.ArgumentParser();p.add_argument('--models',action='store_true');p.add_argument('--python37',action='store_true');args=p.parse_args()
 for item in json.loads((R/'manifests/sota_followup/new_sources.json').read_text()):
  if 'checkout' not in item:continue
  dest=R/item['checkout']
  if not dest.exists():
   dest.mkdir(parents=True);subprocess.run(['git','init','-q',str(dest)],check=True);subprocess.run(['git','-C',str(dest),'remote','add','origin','https://github.com/'+item['repository']+'.git'],check=True);subprocess.run(['git','-C',str(dest),'fetch','--depth','1','origin',item['revision']],check=True);subprocess.run(['git','-C',str(dest),'checkout','--detach',item['revision']],check=True)
  assert subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip()==item['revision']
 for name in ['rt','st']:
  original=Path('/workspace/research_sources/qixuchen__AutoTest/benchmarks')/(name+'_bench.csv');dest=R/f'data/raw/qixuchen__AutoTest/benchmarks/{name}_bench.csv';expected=json.loads((R/f'manifests/sota_followup/{name}_qualification.json').read_text())['sha256'];assert digest(original)==expected
  if not dest.exists():dest.parent.mkdir(parents=True,exist_ok=True);dest.symlink_to(original)
  assert digest(dest)==expected
 if args.python37:
  item=json.loads((R/'evidence/sota_followup/python37_acquisition.json').read_text());fetch(item,R/'data/sota_followup/Miniconda3-py37_23.1.0-1-Linux-x86_64.sh')
 if args.models:
  for item in json.loads((R/'manifests/sota_followup/autotest_materials.json').read_text())+[json.loads((R/'manifests/sota_followup/doduo_checkpoint.json').read_text())]+json.loads((R/'manifests/sota_followup/autotest_lfs_features.json').read_text()):fetch(item,R/item['local_path'])
  for file,dest in [('minilm.json','data/torch_cache/sentence_transformers/sentence-transformers_all-MiniLM-L6-v2'),('bert.json','data/sota_followup/bert_base_uncased')]:
   for item in json.loads((R/'manifests/sota_followup'/file).read_text())['files']:fetch(item,R/dest/item['file'])
  for item in json.loads((R/'manifests/sota_followup/nltk.json').read_text()):
   target=R/item['local_path'];fetch(item,target)
   import zipfile
   with zipfile.ZipFile(target) as z:z.extractall(target.parent)
if __name__=='__main__':main()
