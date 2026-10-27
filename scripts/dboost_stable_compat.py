# SPDX-License-Identifier: GPL-3.0-or-later
"""Explicit dBoost numeric compatibility repair: stable population moments.
The original statistical algorithm is unchanged mathematically. Different rounding
can change threshold-boundary results, so this is named a repaired implementation.
Not substituted into the primary original-code experiment.
"""
import sys,math,statistics,runpy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'data/sources/cpitclaudel__dBoost'))
from dboost.analyzers.utils import Stats
old_update=Stats.update

def stable_update(self,x):
 if not hasattr(self,'_values'):self._values=[]
 self._values.append(x);self.__dict__.pop('_stable_mean',None);self.__dict__.pop('_stable_sigma',None);old_update(self,x)

def stable_pearson(s1,s2,pw_prod):
 if not s1.sigma or not s2.sigma:return None
 cov=math.fsum((x-s1.avg)*(y-s2.avg) for x,y in zip(s1._values,s2._values))/s1.count
 return cov/(s1.sigma*s2.sigma)
Stats.update=stable_update
def mean(self):
 if '_stable_mean' not in self.__dict__:self._stable_mean=math.fsum(self._values)/len(self._values)
 return self._stable_mean
def sigma(self):
 if '_stable_sigma' not in self.__dict__:self._stable_sigma=statistics.pstdev(self._values)
 return self._stable_sigma
Stats.avg=property(mean)
Stats.sigma=property(sigma)
Stats.pearson=staticmethod(stable_pearson)
if __name__=='__main__':runpy.run_path(str(ROOT/'scripts/native_detector_worker.py'),run_name='__main__')
