"""Training-only aggregates; no raw-label paths or partition selector."""
import json
from pathlib import Path

import pandas as pd

from retention_lab.eda_prepare import TRAIN_COLUMNS, fingerprint

CHARTS = {
    'auto_renew': 'Recorded auto-renew configuration',
    'observed_history_days': 'Observed history through January 31 (days)',
    'january_transactions': 'Distinct January transactions',
    'latest_plan_days': 'Latest agreed recorded plan duration (days)',
    'latest_amount': 'Latest agreed recorded amount',
}
NUMERIC = ['observed_history_days', 'january_transactions', 'latest_plan_days',
           'latest_amount', 'distinct_transactions', 'latest_list_price']


def load_training(directory: Path) -> pd.DataFrame:
    """Load only the private training artifact, verify it, then discard IDs.

    This is a pipeline boundary, not an operating-system security sandbox.
    A notebook kernel with filesystem privileges can still access other files.
    """
    quality = json.loads((directory / 'quality.json').read_text())
    path = directory / 'training.csv'
    if fingerprint(path) != quality['training_artifact']:
        raise ValueError('Training artifact fingerprint differs')
    frame = pd.read_csv(path, dtype={'msno': str})
    if list(frame.columns) != TRAIN_COLUMNS or frame['msno'].duplicated().any():
        raise ValueError('Invalid private training schema or duplicate identifiers')
    if len(frame) != quality['training_users']:
        raise ValueError('Training count differs')
    return frame.drop(columns='msno')


def bins(values: pd.Series) -> pd.Series:
    """Training marginal quartiles only; tied values may collapse intervals."""
    known = values.dropna()
    if known.empty:
        return pd.Series('Unknown', index=values.index)
    if known.nunique() == 1:
        return values.map(lambda x: f'{x:g}' if pd.notna(x) else 'Unknown')
    grouped = pd.qcut(values, q=4, duplicates='drop')
    return grouped.astype('object').map(lambda x: str(x) if pd.notna(x) else 'Unknown')


def rates(labels: pd.Series, group: pd.Series) -> list[dict]:
    """Every included person contributes once; unknowns are an explicit group."""
    table = pd.DataFrame({'is_churn': labels, 'group': group}).groupby('group', sort=True)['is_churn'].agg(['count', 'sum'])
    def order(name):
        if str(name).startswith(('(', '[')):
            return (0, float(str(name).split(',')[0][1:]))
        return (1, str(name))

    table = table.loc[sorted(table.index, key=order)]
    return [{'group': str(name), 'users': int(row['count']), 'churners': int(row['sum']),
             'churn_rate': float(row['sum'] / row['count'])} for name, row in table.iterrows()]


def summarize(frame: pd.DataFrame) -> dict:
    """Return only aggregate statistics, never subscriber-level records."""
    if frame.empty or frame['is_churn'].isna().any() or not frame['is_churn'].isin([0, 1]).all():
        raise ValueError('Expected nonempty binary training outcomes')
    charts = {}
    for field in CHARTS:
        group = frame[field].map({0: 'Off', 1: 'On'}).fillna('Unknown') if field == 'auto_renew' else bins(frame[field])
        charts[field] = rates(frame['is_churn'], group)
    transition = pd.Series('Other / unknown', index=frame.index)
    transition.loc[frame['always_auto_on'].eq(1)] = 'Always on'
    transition.loc[frame['auto_on_to_off'].gt(0)] = 'Observed on-to-off'
    distributions = {}
    for field in NUMERIC:
        stats = frame[field].sort_values().describe(percentiles=[.25, .5, .75])
        distributions[field] = {str(k): (float(v) if pd.notna(v) else None) for k, v in stats.items()}
    return {'scope': 'training only', 'training_users': len(frame),
            'churners': int(frame['is_churn'].sum()), 'prevalence': float(frame['is_churn'].mean()),
            'missing_fields': {c: int(v) for c, v in frame.isna().sum().items()},
            'distributions': distributions, 'charts': charts,
            'hypothesis_transition': rates(frame['is_churn'], transition),
            'payment_method_counts': {str(k): int(v) for k, v in frame['latest_payment_method'].fillna('Unknown').value_counts().sort_index(key=lambda idx: idx.astype(str)).items()},
            'quality_totals': {c: int(frame[c].sum()) for c in ['distinct_transactions', 'duplicate_rows',
                                'ambiguous_auto_days', 'expiry_before_event', 'far_future_expiry', 'missing_numeric_fields']}}


def plot_rates(table: list[dict], title: str):
    """Plot aggregate rates with visible denominators; association is not effect."""
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(figsize=(9, 4))
    labels = [f"{r['group']}\nn={r['users']:,}" for r in table]
    ax.bar(labels, [100 * r['churn_rate'] for r in table], color='#285f8f')
    ax.set(ylabel='Observed churn (%)', title=title)
    ax.tick_params(axis='x', labelsize=8)
    fig.tight_layout()
    return fig
