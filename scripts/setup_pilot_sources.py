import argparse,json,subprocess
from pathlib import Path
R=Path(__file__).resolve().parents[1];p=argparse.ArgumentParser();p.add_argument('--all',action='store_true');args=p.parse_args()
for item in json.loads((R/'configs/thesis_pilot/sources.json').read_text()):
 if not args.all and item['repository'] in ['qixuchen/AutoTest','ZJU-Data-Governance-and-Services-Team/ZeroED','ggml-org/llama.cpp']:continue
 dest=Path(item['checkout']);dest=dest if dest.is_absolute() else R/dest
 if dest.exists():
  rev=subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip()
  if rev!=item['revision']:raise ValueError('Existing source differs; refusing to reset '+str(dest))
 else:
  dest.mkdir(parents=True)
  for cmd in [['git','init','-q',str(dest)],['git','-C',str(dest),'remote','add','origin',item['url']],['git','-C',str(dest),'fetch','--depth','1','origin',item['revision']],['git','-C',str(dest),'checkout','--detach',item['revision']]]:subprocess.run(cmd,check=True)
 print(item['repository'],item['revision'])
