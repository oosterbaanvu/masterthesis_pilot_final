"""Pinned byte acquisition: verify before atomic publication, never accept changed bytes."""
import argparse
import concurrent.futures
import hashlib
import json
from pathlib import Path
import urllib.request
import urllib.error
import time

def digest(path):
    h=hashlib.sha256()
    with Path(path).open('rb') as f:
        for chunk in iter(lambda:f.read(1024*1024),b''): h.update(chunk)
    return h.hexdigest()

def acquire_one(item, root, refresh=False):
    dest=Path(root)/item['path']
    if dest.exists() and not refresh:
        if dest.stat().st_size!=item['bytes'] or digest(dest)!=item['sha256']:
            raise ValueError('Existing bytes differ: '+item['path'])
        return {'path':item['path'],'state':'VERIFIED_LOCAL','bytes':dest.stat().st_size,'sha256':digest(dest)}
    dest.parent.mkdir(parents=True,exist_ok=True)
    tmp=dest.with_suffix(dest.suffix+'.partial')
    try:
        for attempt in range(3):
            try:
                with urllib.request.urlopen(item['url'],timeout=90) as source,tmp.open('wb') as out:
                    while chunk:=source.read(1024*1024): out.write(chunk)
                break
            except urllib.error.HTTPError as error:
                if error.code not in {429,502,503,504} or attempt==2: raise
                time.sleep(2**attempt)
        if tmp.stat().st_size!=item['bytes'] or digest(tmp)!=item['sha256']:
            raise ValueError('Remote checksum/size mismatch: '+item['path'])
        tmp.replace(dest)
    finally:
        tmp.unlink(missing_ok=True)
    return {'path':item['path'],'state':'DOWNLOADED_VERIFIED','bytes':dest.stat().st_size,'sha256':digest(dest)}

def main():
    p=argparse.ArgumentParser();p.add_argument('--root',default='.');p.add_argument('--manifest',default='manifests/files.json');p.add_argument('--refresh',action='store_true');p.add_argument('--log',default='evidence/acquisition.json');a=p.parse_args()
    items=json.loads(Path(a.manifest).read_text())
    def run(x):
        try:return acquire_one(x,a.root,a.refresh)
        except Exception as e:return {'path':x['path'],'state':'FAILED','error':str(e)}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool: results=list(pool.map(run,items))
    Path(a.log).parent.mkdir(parents=True,exist_ok=True);Path(a.log).write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps({'files':len(results),'failed':sum(x['state']=='FAILED' for x in results)}))
    if any(x['state']=='FAILED' for x in results): raise SystemExit(1)
if __name__=='__main__':main()
