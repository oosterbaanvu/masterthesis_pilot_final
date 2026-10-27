"""Named CDC compatibility adaptation: declare source types, retain original models/calibration.
This does not claim to reproduce the paper's automatic dtype inference or its scores.
"""
import sys,json,contextlib,traceback
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import native_detector_worker as native
for line in sys.stdin:
 try:
  req=json.loads(line)
  if req['op']=='fit':
   sys.path.insert(0,req['source']);from conformal_data_cleaning.cleaner.conformal import ConformalAutoGluonCleaner
   categories=list(req['categorical'])
   def declared(self,data):
    self._categorical_columns=[c for c in data.columns if c in categories]
    self._numerical_columns=[c for c in data.columns if c not in categories]
   ConformalAutoGluonCleaner._guess_dtypes=declared
  req['method']='cdc_original'
  with contextlib.redirect_stdout(sys.stderr):result=native.dispatch(req)
  result['adaptation']='source-declared numeric/categorical types; native AutoGluon RF/XT and conformal calibration otherwise unchanged'
  print(json.dumps({'ok':True,'result':result},default=lambda x:x.item() if hasattr(x,'item') else str(x)),flush=True)
 except Exception as e:
  traceback.print_exc(file=sys.stderr);print(json.dumps({'ok':False,'error':repr(e)}),flush=True)
