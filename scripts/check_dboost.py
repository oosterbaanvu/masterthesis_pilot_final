"""Upstream smoke test on an explicit fixture, NOT benchmark performance."""
import json,pathlib,subprocess,sys
root=pathlib.Path(__file__).resolve().parents[1]
source=root/'data/sources/cpitclaudel__dBoost'
if len(sys.argv)>1:source=pathlib.Path(sys.argv[1])
sha=subprocess.check_output(['git','-C',str(source),'rev-parse','HEAD'],text=True).strip()
assert sha=='a47cb564e900c3e5220413f810e810b00046d561'
fixture=root/'data/fixtures/dboost.tsv';fixture.parent.mkdir(parents=True,exist_ok=True)
fixture.write_text(''.join(f'{10.0+(i%3)*0.1}\t{20.0+(i%5)*0.1}\n' for i in range(100))+'1000000.0\t20.0\n')
command=[sys.executable,str(source/'dboost/dboost-stdin.py'),'--statistical','0.5','--gaussian','3','--minimal',str(fixture)]
r=subprocess.run(command,capture_output=True,text=True,timeout=60)
result={'revision':sha,'command':command,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'test_kind':'ENGINEERING_FIXTURE_ONLY','granularity':'ROW (upstream --minimal output), not cell','expected_outlier_row':100}
(root/'evidence/dboost_smoke.json').write_text(json.dumps(result,indent=2)+'\n')
assert r.returncode==0 and '100' in r.stdout.splitlines(),result
print('Upstream dBoost identifies extreme fixture row 100; no empirical dataset scores claimed.')
