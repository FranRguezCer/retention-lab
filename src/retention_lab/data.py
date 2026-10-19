"""Cutoff-safe preparation; holdout outcome values are never interpreted."""
from contextlib import closing, contextmanager
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


@contextmanager
def prepared_events(raw: Path, output: Path, expected: tuple[int, int] | None = None):
    """Build shared original-source states and freeze assignments without outcomes.

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
            yield db, scratch, population, manifest


def summarize_history(db: sqlite3.Connection, selection: str) -> dict:
    """Aggregate exact events and renewal transitions using the shared day states."""
    if selection not in ('labels', 'assignment'):
        raise ValueError('Invalid history selection')
    db.execute('CREATE TABLE history AS SELECT e.msno,MIN(e.transaction_date) AS first_day, '
               "SUM(e.transaction_date >= '20170101') AS january, COUNT(*) AS distinct_transactions, "
               'SUM(copies-1) AS duplicates, SUM(membership_expire_date < transaction_date) AS past_expiry, '
               "SUM(membership_expire_date > '20180201') AS far_expiry, "
               "SUM((payment_method_id='')+(payment_plan_days='')+(plan_list_price='')+(actual_amount_paid='')) AS missing "
               f'FROM events e JOIN {selection} USING(msno) GROUP BY e.msno')
    changes = {}
    for user, rows in itertools.groupby(db.execute(
            f'SELECT d.msno,d.is_auto_renew FROM daily d JOIN {selection} USING(msno) ORDER BY d.msno,d.transaction_date'), key=lambda r: r[0]):
        previous, on_off, all_on, ambiguous = None, 0, True, 0
        for _, state in rows:
            on_off += int(previous == '1' and state == '0')
            all_on &= state == '1'
            ambiguous += int(state is None)
            previous = state  # An ambiguous day breaks the transition chain.
        changes[user] = (on_off, int(all_on), ambiguous)
    return changes
