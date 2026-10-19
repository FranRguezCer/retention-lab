"""Cutoff-safe EDA preparation; holdout outcome values are never interpreted."""
import csv
import hashlib
import json
from pathlib import Path

from retention_lab.data import (  # Preserve the established helper imports.
    COLUMNS, SALT, CUTOFF, calendar, fingerprint, prepared_events,
    publish_private, read_rows, split_user, write_json, summarize_history,
)

TRAIN_COLUMNS = ['msno', 'is_churn', 'auto_renew', 'observed_history_days',
                 'january_transactions', 'latest_plan_days', 'latest_amount',
                 'auto_on_to_off', 'always_auto_on', 'distinct_transactions',
                 'duplicate_rows', 'ambiguous_auto_days', 'expiry_before_event',
                 'far_future_expiry', 'missing_numeric_fields', 'latest_list_price',
                 'latest_payment_method']


def prepare(raw: Path, output: Path, expected: tuple[int, int] | None = None) -> dict:
    """Freeze shared assignments, then extract training-only EDA observations."""
    with prepared_events(raw, output, expected) as (db, scratch, population, manifest):
        db.execute('CREATE TABLE labels (msno TEXT PRIMARY KEY, is_churn INTEGER) WITHOUT ROWID')
        train_ids = {u for (u,) in db.execute("SELECT msno FROM assignment WHERE partition='train'")}
        seen_ids = hashlib.sha256()
        db.execute('CREATE TABLE reread_ids (msno TEXT PRIMARY KEY) WITHOUT ROWID')
        for user, value in read_rows(raw / 'train.csv', ['msno', 'is_churn']):
            db.execute('INSERT INTO reread_ids VALUES (?)', (user,))
            if user in train_ids:
                if value not in ('0', '1'):
                    raise ValueError('Invalid training label')
                db.execute('INSERT INTO labels VALUES (?,?)', (user, int(value)))
        for (user,) in db.execute('SELECT msno FROM reread_ids ORDER BY msno'):
            seen_ids.update((json.dumps(user) + '\n').encode())
        if seen_ids.hexdigest() != manifest['sources']['train.csv']['sorted_identifier_sha256'] or db.execute('SELECT COUNT(*) FROM labels').fetchone()[0] != len(train_ids):
            raise ValueError('Label identifier coverage changed')
        del train_ids
        changes = summarize_history(db, 'labels')
        training = scratch / 'training.csv'
        query = ('SELECT l.msno,y.is_churn,l.is_auto_renew,h.first_day,h.january,l.payment_plan_days,'
                 'l.actual_amount_paid,h.distinct_transactions,h.duplicates,h.past_expiry,h.far_expiry,h.missing,'
                 'l.plan_list_price,l.payment_method_id FROM latest l JOIN labels y USING(msno) '
                 'JOIN history h USING(msno) ORDER BY l.msno')
        with training.open('w', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(TRAIN_COLUMNS)
            for u, label, auto, first, jan, days, amount, n, dup, past, far, missing, price, method in db.execute(query):
                transitions, all_on, ambiguous = changes[u]
                history_days = (calendar(CUTOFF) - calendar(first)).days
                writer.writerow([u, label, auto, history_days, jan, days, amount, transitions, all_on,
                                 n, dup, ambiguous, past, far, missing, price, method])
        quality = {'scope': 'training only, cutoff-safe exact distinct transactions',
                   'training_users': len(changes), 'training_artifact': fingerprint(training),
                   'totals': dict(zip(['distinct_transactions', 'duplicate_rows', 'expiry_before_event',
                                      'expiry_after_20180201', 'missing_numeric_fields'],
                                     db.execute('SELECT SUM(distinct_transactions),SUM(duplicates),SUM(past_expiry),SUM(far_expiry),SUM(missing) FROM history').fetchone()))}
        write_json(scratch / 'quality.json', quality)
        for name in ('training.csv', 'quality.json'):
            publish_private(output / name, scratch / name)
    return population
