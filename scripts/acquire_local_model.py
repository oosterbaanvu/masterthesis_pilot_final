"""Optional public local model, pinned revision and publisher LFS checksum."""
import hashlib,json,urllib.request
from pathlib import Path
R=Path(__file__).resolve().parents[1];repo='Qwen/Qwen3-0.6B-GGUF';rev='23749fefcc72300e3a2ad315e1317431b06b590a';name='Qwen3-0.6B-Q8_0.gguf';sha='9465e63a22add5354d9bb4b99e90117043c7124007664907259bd16d043bb031';size=639446688
p=R/'data/models'/name;p.parent.mkdir(exist_ok=True);temp=p.with_suffix('.partial');url=f'https://huggingface.co/{repo}/resolve/{rev}/{name}'
if not p.exists() or p.stat().st_size!=size or hashlib.sha256(p.read_bytes()).hexdigest()!=sha:
 try:
  with urllib.request.urlopen(url,timeout=120) as source,temp.open('wb') as out:
   while chunk:=source.read(1024*1024):out.write(chunk)
  assert temp.stat().st_size==size and hashlib.sha256(temp.read_bytes()).hexdigest()==sha
  temp.replace(p)
 finally:temp.unlink(missing_ok=True)
metadata={'model':repo,'revision':rev,'file':name,'quantization':'Q8_0','bytes':size,'sha256':sha,'expected_lfs_sha256':sha,'url':url,'license':'Apache-2.0 per official model card','status':'VERIFIED','scope':'0.6B local rule-generation engineering experiment, not reproduction of ZeroED Qwen2.5-72B'}
(R/'evidence/thesis_pilot/local_model_acquisition.json').write_text(json.dumps(metadata,indent=2));print(metadata)
