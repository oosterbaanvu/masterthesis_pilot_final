"""Information boundaries and reference-relative set metrics, not semantic truth certification."""
from dataclasses import dataclass
from math import isfinite

@dataclass(frozen=True)
class DirtyTable:
    columns: tuple[str,...]
    rows: tuple[tuple[str,...],...]
    role: str='dirty_features'
    def validate(self, allowed):
        forbidden={'ground_truth','ground_truth_debatable','reference','clean','label','is_error','error_location','fraud_bool','default.payment.next.month','y','class'}
        if self.role!='dirty_features' or set(self.columns)!=set(allowed) or len(self.columns)!=len(allowed):
            raise ValueError('Unapproved feature population or role')
        if any(c.casefold() in forbidden for c in self.columns):raise ValueError('Reference/label/outcome columns forbidden')
        if any(len(r)!=len(self.columns) for r in self.rows):raise ValueError('Ragged feature rows')

def compatibility(method, granularity, labelled_reference=False, clean_history=False):
    if method=='cdc':return 'CONDITIONAL' if granularity=='cell' and clean_history else 'INCOMPATIBLE'
    if method=='raha':return 'CONDITIONAL' if granularity=='cell' and labelled_reference else 'INCOMPATIBLE'
    if method=='dboost':return 'COMPATIBLE' if granularity=='cell' else 'INCOMPATIBLE'
    if method=='isolation_forest':return 'COMPATIBLE' if granularity=='row' else 'INCOMPATIBLE'
    if method=='autotest_sdc':return 'CONDITIONAL' if granularity=='column_value' else 'INCOMPATIBLE'
    raise ValueError('Unreviewed method')

def evaluate(universe,positives,ignored,controls,learned):
    universe,positives,ignored,controls,learned=map(set,[universe,positives,ignored,controls,learned])
    if positives&ignored or not (positives|ignored|controls|learned)<=universe:raise ValueError('Invalid target/coordinate population')
    def metrics(alerts):
        scored=alerts-ignored;tp=len(scored&positives);fp=len(scored-positives);fn=len(positives-scored)
        return {'tp':tp,'fp_reference_relative':fp,'fn':fn,'precision':tp/len(scored) if scored else None,'recall':tp/len(positives) if positives else None,'f1':2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else None,'alerts':len(alerts),'unscored_alerts':len(alerts&ignored)}
    extra=learned-controls
    scored_extra=extra-ignored
    return {'controls':metrics(controls),'union':metrics(controls|learned),'additional_alerts':len(extra),'additional_reference_hits':len(extra&positives),'marginal_precision':len(extra&positives)/len(scored_extra) if scored_extra else None,'additional_unscored':len(extra&ignored)}

def budget_review(order,budget,universe):
    if len(order)!=len(set(order)) or not set(order)<=set(universe) or budget<0:raise ValueError('Invalid review schedule')
    return set(order[:budget])

def run_rules(table,allowed,contract):
    table.validate(allowed);alerts=set()
    for i,row in enumerate(table.rows):
        for j,(col,value) in enumerate(zip(table.columns,row)):
            spec=contract.get(col,{})
            if value in spec.get('missing_tokens',[]): alerts.add((i,j));continue
            if 'permitted_values' in spec and value not in spec['permitted_values']:alerts.add((i,j))
            if spec.get('numeric'):
                try:
                    x=float(value)
                    if not isfinite(x) or ('bounds' in spec and not spec['bounds'][0]<=x<=spec['bounds'][1]):alerts.add((i,j))
                except ValueError:alerts.add((i,j))
    return alerts
