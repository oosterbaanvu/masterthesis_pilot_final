"""Reconstruct pinned source checkouts in ignored local storage, never update an existing checkout."""
import argparse,json,pathlib,subprocess
p=argparse.ArgumentParser();p.add_argument('--only',default=None);a=p.parse_args()
for item in json.loads(pathlib.Path('evidence/source_acquisition.json').read_text()):
 repo=item['repository'];sha=item.get('sha')
 if not sha or (a.only and a.only!=repo):continue
 dest=pathlib.Path('data/sources')/repo.replace('/','__')
 if dest.exists():
  actual=subprocess.check_output(['git','-C',str(dest),'rev-parse','HEAD'],text=True).strip()
  if actual!=sha:raise ValueError('Refusing to alter existing checkout: '+str(dest))
  continue
 dest.mkdir(parents=True)
 for cmd in [['git','init','-q',str(dest)],['git','-C',str(dest),'remote','add','origin','https://github.com/'+repo+'.git'],['git','-C',str(dest),'fetch','--depth','1','origin',sha],['git','-C',str(dest),'checkout','--detach',sha]]:
  subprocess.run(cmd,check=True,timeout=240)
print('Pinned sources verified. No historical experimental conclusions were rerun.')
