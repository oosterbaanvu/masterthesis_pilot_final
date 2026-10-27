"""Recreate compatibility-only working copy from pinned author source, without vendoring."""
import hashlib,json,re,shutil
from pathlib import Path
R=Path(__file__).resolve().parents[1];S=Path('/workspace/research_sources/qixuchen__AutoTest/code/AutoTest');D=R/'data/sota_followup/autotest37_source';records=[]
if not D.exists():shutil.copytree(S,D,symlinks=True)
for relative in ['config.py','STEP3_SDC_application.py','demo/demo_utils/demo_util.py','sherlock-project/sherlock/features/paragraph_vectors.py','doduo-project/doduo/doduo.py']:
 src=S/relative;dest=D/relative;text=src.read_text()
 if relative=='config.py':text=text.replace("'/home/azureuser/AutoTest'",repr(str(D))).replace("'/datadrive/qixu'",repr(str(R/'data/sota_followup/autotest_storage')))
 if relative in ['STEP3_SDC_application.py','demo/demo_utils/demo_util.py']:text=re.sub(r'n_proc = (?:48|32|15|8)\b','n_proc = 2',text)
 if relative=='demo/demo_utils/demo_util.py':
  line='            sbert_dist_val_embeddings = pickle.load(file)';text=text.replace(line,line+'\n        sbert_dist_val_embeddings = sbert_dist_val_embeddings.loc[benchmark.index] if hasattr(sbert_dist_val_embeddings,"loc") else pd.Series(sbert_dist_val_embeddings).loc[benchmark.index]');line='        doduo_dist_val_scores = pd.read_pickle(doduo_dist_val_scores_fname)';text=text.replace(line,line+'\n        doduo_dist_val_scores = doduo_dist_val_scores.loc[benchmark.index]')
 if relative.endswith('paragraph_vectors.py'):
  text=text.replace('import random\n','import random\nimport os\n')
  text=text.replace('nltk.download("punkt")','nltk.download("punkt",download_dir=os.environ["NLTK_DATA"])').replace('nltk.download("stopwords")','nltk.download("stopwords",download_dir=os.environ["NLTK_DATA"])')
 if relative.endswith('doduo.py'):text=text.replace('self.args.shortcut_name = "bert-base-uncased"','self.args.shortcut_name = '+repr(str(R/'data/sota_followup/bert_base_uncased')))
 if dest.read_text() not in [src.read_text(),text]:raise RuntimeError('Unknown local edits; refusing to overwrite '+relative)
 dest.write_text(text);records.append({'file':relative,'upstream_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'working_sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
def link(src,dest):
 dest.parent.mkdir(parents=True,exist_ok=True)
 if dest.is_symlink():
  if dest.resolve()==src.resolve():return
  raise RuntimeError('Different existing symlink '+str(dest))
 if dest.exists():
  if hashlib.sha256(dest.read_bytes()).digest()==hashlib.sha256(src.read_bytes()).digest():return
  # Released demo embeddings are Git LFS pointers, replaced only with verified objects.
  if not dest.read_bytes().startswith(b'version https://git-lfs.github.com/spec/v1'):raise RuntimeError('Different existing material '+str(dest))
  dest.unlink()
 dest.symlink_to(src)
items=json.loads((R/'manifests/sota_followup/autotest_materials.json').read_text())+[json.loads((R/'manifests/sota_followup/doduo_checkpoint.json').read_text())]
for item in items:
 source=R/item['local_path'];path=item['source_path']
 if '/features/' in path:dest=D/'sherlock-project/sherlock/features'/Path(path).name
 elif '/sherlock-materials/' in path:dest=D/'sherlock-project/model_files'/Path(path).name
 else:dest=D/'doduo-project/model'/Path(path).name
 link(source,dest)
for name in ['rt','st']:link(R/f'data/sota_followup/{name}_bench_dist_val_embeddings.pkl',D/f'demo/cache/{name}_bench_dist_val_embeddings.pkl')
store=R/'data/sota_followup/autotest_storage'
for name,internal in [('rt','labeled_benchmark'),('st','excel_benchmark')]:
 for kind,folder,suffix,ext in [('sbert','sbert_dist_embedding','dist_val_embeddings','pkl'),('doduo','doduo','dist_val_scores','pickle')]:
  src=D/f'demo/cache/{name}_bench_{suffix}.{ext}';dest=store/folder/f'{internal}_{suffix}.{ext}'
  if not dest.exists():link(src,dest) # preserve explicit input-repaired caches
link(D/'sherlock-project/sherlock/features/glove.6B.50d.txt',store/'GLoVe/glove.6B.50d.txt')
(R/'manifests/sota_followup/autotest_working_files.json').write_text(json.dumps(records,indent=2)+'\n');print('Working copy transformations and verified material paths ready')
