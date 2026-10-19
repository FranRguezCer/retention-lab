"""Cutoff-safe preparation; holdout outcome values are never interpreted."""
from contextlib import closing
import csv
from datetime import datetime
from functools import lru_cache
import hashlib
import itertools
import json
from pathlib import Path
import sqlite3
import tempfile

COLUMNS = ('msno payment_method_id payment_plan_days plan_list_price '
           'actual_amount_paid is_auto_renew transaction_date '
           'membership_expire_date is_cancel').split()
SALT = 'retention-lab-feb2017-v1|'
CUTOFF = '20170131'
TRAIN_COLUMNS = ['msno', 'is_churn', 'auto_renew', 'observed_history_days',
                 'january_transactions', 'latest_plan_days', 'latest_amount',
                 'auto_on_to_off', 'always_auto_on', 'distinct_transactions',
                 'duplicate_rows', 'ambiguous_auto_days', 'expiry_before_event',
                 'far_future_expiry', 'missing_numeric_fields', 'latest_list_price',
                 'latest_payment_method']


def fingerprint(path: Path) -> dict:
    """Fingerprint bytes without retaining source records."""
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(chunk)
    return {'sha256': h.hexdigest(), 'size_bytes': path.stat().st_size}


def split_user(user: str) -> tuple[str, int, str]:
    """Apply the approved digest and bucket mapping, without outcomes."""
    digest = hashlib.sha256((SALT + user).encode('utf-8')).hexdigest()
    bucket = int(digest, 16) % 10
    return digest, bucket, 'train' if bucket < 6 else 'validation' if bucket < 8 else 'final'


@lru_cache(maxsize=8192)
def calendar(value: str) -> datetime:
    """Reject invalid dates; future recorded expiry itself is permitted."""
    if len(value) != 8 or not value.isascii() or not value.isdigit():
        raise ValueError('Invalid date')
    return datetime.strptime(value, '%Y%m%d')


def read_rows(path: Path, columns: list[str]):
    """Stream structurally checked rows, without logging private values."""
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.reader(stream, strict=True)
        if next(reader, None) != columns:
            raise ValueError('Unexpected schema')
        for row in reader:
            if len(row) != len(columns) or not row[0]:
                raise ValueError('Invalid row')
            yield row


def publish_private(path: Path, candidate: Path) -> None:
    """Create once, or verify identical bytes; never replace changed evidence."""
    if path.exists():
        if fingerprint(path) != fingerprint(candidate):
            raise ValueError('Existing private artifact differs')
    else:
        with path.open('xb') as target, candidate.open('rb') as source:
            for chunk in iter(lambda: source.read(1024 * 1024), b''):
                target.write(chunk)


def write_json(path: Path, content: dict) -> None:
    path.write_text(json.dumps(content, sort_keys=True, indent=2) + '\n')


def prepare(raw: Path, output: Path, expected: tuple[int, int] | None = None) -> dict:
    """Freeze assignments first, then extract and summarize training labels only.

    SQLite retains exact full-field keys on disk. Source label provenance uses
    sorted identifiers, deliberately excluding non-training outcome bytes.
    """
    source = raw / 'transactions.csv'
    before = fingerprint(source)
    output.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='retention-eda-') as directory:
        scratch = Path(directory)
        with closing(sqlite3.connect(scratch / 'events.sqlite')) as db:
            db.execute('PRAGMA journal_mode=OFF')
            db.execute('PRAGMA synchronous=OFF')
            db.execute('PRAGMA temp_store=FILE')
            db.execute('PRAGMA cache_size=-65536')
            db.execute('CREATE TABLE ids (msno TEXT PRIMARY KEY) WITHOUT ROWID')
            # The second field is transported by CSV parsing, never evaluated.
            db.executemany('INSERT INTO ids VALUES (?)',
                           ((row[0],) for row in read_rows(raw / 'train.csv', ['msno', 'is_churn'])))
            ids_hash = hashlib.sha256()
            for (user,) in db.execute('SELECT msno FROM ids ORDER BY msno'):
                ids_hash.update((json.dumps(user) + '\n').encode())
            db.execute('CREATE TABLE events (' + ','.join(c + ' TEXT' for c in COLUMNS)
                       + ', copies INTEGER NOT NULL DEFAULT 1, PRIMARY KEY ('
                       + ','.join(['msno', 'transaction_date'] + [c for c in COLUMNS if c not in ('msno', 'transaction_date')])
                       + ')) WITHOUT ROWID')

            def transactions():
                for row in read_rows(source, COLUMNS):
                    calendar(row[6])
                    if row[6] > CUTOFF:
                        continue
                    calendar(row[7])
                    if row[5] not in ('0', '1') or row[8] not in ('0', '1'):
                        raise ValueError('Invalid flag')
                    for index in (1, 2, 3, 4):
                        if row[index]:
                            int(row[index])
                    yield row

            db.executemany('INSERT INTO events (' + ','.join(COLUMNS)
                           + ') VALUES (' + ','.join('?' for _ in COLUMNS)
                           + ') ON CONFLICT DO UPDATE SET copies=copies+1', transactions())
            db.commit()
            # All fields have independent agreement checks, never row-order ties.
            agreed = lambda c: f'CASE WHEN MIN({c})=MAX({c}) THEN MIN({c}) END AS {c}'
            db.execute('CREATE TABLE daily AS SELECT msno, transaction_date, '
                       + ','.join(agreed(c) for c in COLUMNS if c not in ('msno', 'transaction_date'))
                       + ',COUNT(*) AS distinct_rows FROM events GROUP BY msno,transaction_date')
            db.execute('CREATE UNIQUE INDEX daily_key ON daily(msno,transaction_date)')
            db.execute('CREATE TABLE latest AS SELECT d.* FROM daily d JOIN '
                       '(SELECT msno,MAX(transaction_date) AS day FROM daily GROUP BY msno) l '
                       'ON d.msno=l.msno AND d.transaction_date=l.day')
            predicate = "membership_expire_date BETWEEN '20170201' AND '20170228' AND is_cancel='0' AND is_auto_renew IS NOT NULL"
            candidates = db.execute('SELECT COUNT(*) FROM latest WHERE ' + predicate).fetchone()[0]
            db.execute('CREATE TABLE assignment (msno TEXT PRIMARY KEY,digest TEXT,bucket INTEGER,partition TEXT) WITHOUT ROWID')
            eligible = db.execute('SELECT l.msno FROM latest l JOIN ids USING(msno) WHERE ' + predicate + ' ORDER BY l.msno')
            db.executemany('INSERT INTO assignment VALUES (?,?,?,?)',
                           ((u, *split_user(u)) for (u,) in eligible))
            counts = dict(db.execute('SELECT partition,COUNT(*) FROM assignment GROUP BY partition'))
            total = sum(counts.values())
            if expected is not None and (candidates, total) != expected:
                raise ValueError('Unexpected real population')
            if db.execute('SELECT COUNT(DISTINCT msno) FROM assignment').fetchone()[0] != total:
                raise ValueError('Partition coverage failure')
            if before != fingerprint(source):
                raise ValueError('Source changed')
            population = {'candidates': candidates, 'labeled': total, 'unlabeled': candidates - total,
                          'partitions': counts,
                          'proportions': {k: v / total for k, v in counts.items()} if total else {}}
            manifest = {'version': 1, 'configuration': {'cutoff': CUTOFF, 'salt': SALT,
                        'buckets': {'train': [0, 5], 'validation': [6, 7], 'final': [8, 9]},
                        'deduplication': 'exact all CSV fields', 'schema': COLUMNS},
                        'sources': {'transactions.csv': before,
                                    'train.csv': {'sorted_identifier_sha256': ids_hash.hexdigest(),
                                                  'fingerprint_scope': 'identifiers only; no outcome values'}},
                        'population': population}
            assignments = scratch / 'assignments.csv'
            with assignments.open('w', newline='') as stream:
                writer = csv.writer(stream)
                writer.writerow(['msno', 'digest', 'bucket', 'partition'])
                writer.writerows(db.execute('SELECT * FROM assignment ORDER BY msno'))
            manifest['assignments'] = fingerprint(assignments)
            write_json(scratch / 'manifest.json', manifest)
            # Both artifacts are materialized and verified BEFORE label extraction.
            for name in ('manifest.json', 'assignments.csv'):
                publish_private(output / name, scratch / name)
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
            if seen_ids.hexdigest() != ids_hash.hexdigest() or db.execute('SELECT COUNT(*) FROM labels').fetchone()[0] != len(train_ids):
                raise ValueError('Label identifier coverage changed')
            del train_ids
            db.execute('CREATE TABLE history AS SELECT e.msno,MIN(e.transaction_date) AS first_day, '
                       "SUM(e.transaction_date >= '20170101') AS january, COUNT(*) AS distinct_transactions, "
                       'SUM(copies-1) AS duplicates, SUM(membership_expire_date < transaction_date) AS past_expiry, '
                       "SUM(membership_expire_date > '20180201') AS far_expiry, "
                       "SUM((payment_method_id='')+(payment_plan_days='')+(plan_list_price='')+(actual_amount_paid='')) AS missing "
                       'FROM events e JOIN labels USING(msno) GROUP BY e.msno')
            changes = {}
            for user, rows in itertools.groupby(db.execute(
                    'SELECT d.msno,d.is_auto_renew FROM daily d JOIN labels USING(msno) ORDER BY d.msno,d.transaction_date'), key=lambda r: r[0]):
                previous, on_off, all_on, ambiguous = None, 0, True, 0
                for _, state in rows:
                    on_off += int(previous == '1' and state == '0')
                    all_on &= state == '1'
                    ambiguous += int(state is None)
                    previous = state  # An ambiguous day breaks the transition chain.
                changes[user] = (on_off, int(all_on), ambiguous)
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
