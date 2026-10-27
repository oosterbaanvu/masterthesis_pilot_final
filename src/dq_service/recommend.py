"""Conservative bounded recommendations; suspicion is insufficient for adoption."""

def recommend(evidence):
 scope=evidence.get('scope','unspecified')
 result={'scope':scope,'recommendation':'INSUFFICIENT_EVIDENCE','external_validity':evidence.get('external_validity','unestablished')}
 if evidence.get('complete_stipulated_contract_population') and evidence.get('baseline_recall')==1 and evidence.get('maximum_additional_verified_hits')==0:
  return result|{'recommendation':'DO_NOT_ADOPT','reason':'For these stipulated error families existing controls already detect every verified violation; extra detector cost has no unconstrained detection benefit. This does not cover other error types or new sources.'}
 if evidence.get('reference_kind')!='independently_verified_semantic_errors' or not evidence.get('target_population_match'):
  return result|{'reason':'Synthetic changes, uncertain references or unmatched populations cannot justify operational adoption.'}
 lower=evidence.get('lower_additional_useful_hits');upper=evidence.get('upper_additional_useful_hits');cost=evidence.get('upper_reviews_per_useful_hit');limit=evidence.get('maximum_acceptable_reviews_per_useful_hit')
 if upper is not None and upper<=0:return result|{'recommendation':'DO_NOT_ADOPT','reason':'No positive incremental useful detections supported in the specified population.'}
 if lower is not None and lower>0 and cost is not None and limit is not None and cost<=limit:return result|{'recommendation':'ADOPT','reason':'Verified positive incremental benefit and acceptable measured review burden within the explicitly matched population.'}
 return result|{'reason':'Uncertainty or measured review cost remains unresolved.'}
