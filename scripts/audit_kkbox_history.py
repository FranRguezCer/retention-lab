"""Audit four KKBOX sources; emit aggregates, never modeling rows or IDs.

Full-row SHA-256 sets grow with distinct rows (several GB for the real history).
No effective-expiry ordering, labels or predictive features are reconstructed.
"""
import argparse
from collections.abc import Iterator
from collections import Counter
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sys

from audit_kkbox import DATE_COLUMNS, SCHEMAS, fingerprint

FILES = ('train.csv', 'train_v2.csv', 'transactions.csv', 'transactions_v2.csv')
CUTOFFS = {'20170131': ('20170201', '20170228'),
           '20170228': ('20170301', '20170331')}


def rows(path: Path, header: list[str]) -> Iterator[list[str]]:
    """Yield strict CSV records; errors must not disclose record contents."""
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.reader(stream, strict=True)
        if next(reader, None) != header:
            raise ValueError('Unexpected schema')
        for row in reader:
            if len(row) != len(header):
                raise ValueError('Unexpected row width')
            yield row


def calendar_date(value: str) -> bool:
    """Recognize strict ASCII YYYYMMDD calendar dates."""
    if len(value) != 8 or not value.isascii() or not value.isdigit():
        return False
    try:
        datetime.strptime(value, '%Y%m%d')
    except ValueError:
        return False
    return True


def update_snapshot(snapshot: dict, user: str, day: str, state: tuple) -> None:
    """Count ambiguous latest-day states without guessing intraday order."""
    previous = snapshot.get(user)
    if previous is None or day > previous[0]:
        snapshot[user] = (day, state, False)
    elif day == previous[0] and state != previous[1]:
        snapshot[user] = (day, previous[1], True)


def summarize_cutoffs(snapshots: dict, cohorts: dict) -> dict:
    """Describe observed record states, not official entitlement eligibility."""
    result = {}
    for cutoff, snapshot in snapshots.items():
        low, high = CUTOFFS[cutoff]
        candidates = {u for u, (_, state, ambiguous) in snapshot.items()
                      if not ambiguous and low <= state[0] <= high}
        non_cancelled = {u for u in candidates if snapshot[u][1][1] == '0'}
        summary = {'users_with_history': len(snapshot),
            'ambiguous_latest_day': sum(s[2] for s in snapshot.values()),
            'unambiguous_expiry_in_next_month': len(candidates),
            'non_cancelled_expiry_in_next_month': len(non_cancelled), 'cohorts': {}}
        for name, members in cohorts.items():
            history = members.keys() & snapshot.keys()
            summary['cohorts'][name] = {'with_history': len(history),
                'without_history': len(members) - len(history),
                'ambiguous_latest_day': sum(snapshot[u][2] for u in history),
                'unambiguous_expiry_in_next_month': len(members.keys() & candidates),
                'non_cancelled_expiry_in_next_month': len(members.keys() & non_cancelled)}
        result[cutoff] = summary
    return result


def audit_history(raw: Path, destination: Path) -> bool:
    """Create or verify deterministic evidence for the four unchanged sources."""
    if destination.resolve().is_relative_to(raw.resolve()):
        raise ValueError('Reports must be outside raw data')
    before = {name: fingerprint(raw / name) for name in FILES}
    report = {'audit_version': 2, 'configuration': {
        'cutoffs': CUTOFFS, 'row_identity': 'SHA256(canonical JSON array of CSV fields)',
        'state_identity': ['membership_expire_date', 'is_cancel', 'is_auto_renew'],
        'snapshots': 'diagnostic only; ambiguous latest-day state excluded from expiry matches',
    }, 'files': {}}
    cohorts = {}
    valid = True
    for name in FILES[:2]:
        header = SCHEMAS['train_v2.csv']
        members = {}
        labels = Counter({'0': 0, '1': 0, 'invalid': 0})
        missing = Counter(dict.fromkeys(header, 0))
        duplicates = conflicts = count = 0
        for row in rows(raw / name, header):
            count += 1
            for col, value in zip(header, row):
                missing[col] += int(not value.strip())
            user, label = row
            labels[label if label in ('0', '1') else 'invalid'] += 1
            if user in members:
                duplicates += 1
                conflicts += int(members[user] != label)
            members[user] = label
        cohorts[name] = members
        report['files'][name] = {**before[name], 'columns': header, 'rows': count,
            'unique_ids': len(members), 'duplicate_ids': duplicates,
            'conflicting_label_rows': conflicts, 'missing': dict(missing),
            'labels': dict(labels)}
        valid &= (count > 0 and not duplicates and not labels['invalid']
                  and not any(missing.values()))
    shared = cohorts['train.csv'].keys() & cohorts['train_v2.csv'].keys()
    pairs = Counter(cohorts['train.csv'][u] + '->' + cohorts['train_v2.csv'][u] for u in shared)
    report['cohort_overlap'] = {'shared_ids': len(shared), 'label_pairs': dict(pairs),
        'only_train_ids': len(cohorts['train.csv']) - len(shared),
        'only_train_v2_ids': len(cohorts['train_v2.csv']) - len(shared)}
    del shared
    snapshots = {cutoff: {} for cutoff in CUTOFFS}
    source_hashes = []
    source_users = []
    date_cache = {}
    matching_rows = 0
    for name in FILES[2:]:
        header = SCHEMAS['transactions_v2.csv']
        hashes = set()
        users = set()
        months = Counter()
        flags = Counter()
        missing = Counter(dict.fromkeys(header, 0))
        dates = {col: {'min': None, 'max': None, 'invalid': 0} for col in DATE_COLUMNS}
        count = invalid_flags = expiry_before = distant_expiry = duplicates = 0
        cutoff_rows = Counter(dict.fromkeys(CUTOFFS, 0))
        for row in rows(raw / name, header):
            count += 1
            user, _, _, _, _, auto, day, expiry, cancel = row
            users.add(user)
            for col, value in zip(header, row):
                missing[col] += int(not value.strip())
            identity = hashlib.sha256(json.dumps(row, separators=(',', ':'),
                                                 ensure_ascii=True).encode()).digest()
            duplicates += int(identity in hashes)
            if source_hashes and identity in source_hashes[0]:
                matching_rows += 1
            hashes.add(identity)
            good_dates = True
            for col, value in (('transaction_date', day), ('membership_expire_date', expiry)):
                if value not in date_cache:
                    date_cache[value] = calendar_date(value)
                stats = dates[col]
                if not date_cache[value]:
                    stats['invalid'] += 1
                    good_dates = False
                else:
                    stats['min'] = min(stats['min'] or value, value)
                    stats['max'] = max(stats['max'] or value, value)
            flags[cancel + ',' + auto] += 1
            invalid_flags += int(cancel not in ('0', '1') or auto not in ('0', '1'))
            if good_dates:
                months[day[:6]] += 1
                expiry_before += int(expiry < day)
                distant_expiry += int(expiry > '20201231')
                for cutoff, snapshot in snapshots.items():
                    if day <= cutoff:
                        cutoff_rows[cutoff] += 1
                        update_snapshot(snapshot, user, day, (expiry, cancel, auto))
        report['files'][name] = {**before[name], 'columns': header, 'rows': count,
            'unique_ids': len(users), 'distinct_row_hashes': len(hashes),
            'duplicate_rows': duplicates, 'missing': dict(missing), 'dates': dates,
            'transaction_month_counts': dict(months), 'flag_counts_cancel_auto': dict(flags),
            'invalid_flags': invalid_flags, 'expiry_before_transaction_rows': expiry_before,
            'expiry_after_2020_rows': distant_expiry, 'rows_on_or_before': dict(cutoff_rows)}
        valid &= count > 0 and not any(missing.values()) and not invalid_flags
        valid &= not any(s['invalid'] for s in dates.values())
        source_hashes.append(hashes)
        source_users.append(users)
        if name == 'transactions.csv':
            report['original_cutoffs'] = summarize_cutoffs(snapshots, cohorts)
    overlap = len(source_hashes[0] & source_hashes[1])
    report['transaction_overlap'] = {'shared_distinct_row_hashes': overlap,
        'v2_rows_matching_history': matching_rows,
        'union_distinct_row_hashes': len(source_hashes[0]) + len(source_hashes[1]) - overlap}
    report['transaction_user_overlap'] = len(source_users[0] & source_users[1])
    del source_hashes, source_users
    report['cutoffs'] = summarize_cutoffs(snapshots, cohorts)
    if before != {name: fingerprint(raw / name) for name in FILES}:
        raise ValueError('Sources changed during audit')
    report['source_hashes_unchanged'] = True
    report['valid'] = bool(valid)
    write_report(destination, report)
    return bool(valid)


def write_report(destination: Path, report: dict) -> None:
    """Create aggregate evidence or require identical existing bytes."""
    payload = (json.dumps(report, indent=2, sort_keys=True) + '\n').encode()
    if destination.exists():
        if destination.read_bytes() != payload:
            raise ValueError('Existing report differs; choose a new report path')
    else:
        destination.parent.mkdir(parents=True, exist_ok=True)
        with destination.open('xb') as stream:
            stream.write(payload)


def audit_february_population(raw: Path, destination: Path) -> bool:
    """Check target-class viability of the chosen original-only study subset."""
    if destination.resolve().is_relative_to(raw.resolve()):
        raise ValueError('Reports must be outside raw data')
    names = ('train.csv', 'transactions.csv')
    before = {name: fingerprint(raw / name) for name in names}
    members = {}
    for user, label in rows(raw / 'train.csv', SCHEMAS['train_v2.csv']):
        if not user.strip() or label not in ('0', '1') or user in members:
            raise ValueError('Invalid original labels')
        members[user] = label
    snapshot = {}
    dates = {}
    for row in rows(raw / 'transactions.csv', SCHEMAS['transactions_v2.csv']):
        user, _, _, _, _, auto, day, expiry, cancel = row
        for value in (day, expiry):
            if value not in dates:
                dates[value] = calendar_date(value)
            if not dates[value]:
                raise ValueError('Invalid original dates')
        if not user.strip() or cancel not in ('0', '1') or auto not in ('0', '1'):
            raise ValueError('Invalid original state')
        if day <= '20170131':
            update_snapshot(snapshot, user, day, (expiry, cancel, auto))
    candidates = {user for user, (_, state, ambiguous) in snapshot.items()
                  if not ambiguous and '20170201' <= state[0] <= '20170228'
                  and state[1] == '0'}
    labels = Counter({'0': 0, '1': 0})
    for user in candidates & members.keys():
        labels[members[user]] += 1
    if before != {name: fingerprint(raw / name) for name in names}:
        raise ValueError('Sources changed during population audit')
    report = {'audit_version': 1, 'purpose': 'original-only February subset viability',
        'source_fingerprints': before, 'source_hashes_unchanged': True,
        'configuration': {'cutoff': '20170131', 'expiry_window': CUTOFFS['20170131'],
                          'is_cancel': '0', 'exclude_ambiguous_latest_day': True},
        'candidate_users': len(candidates), 'labeled_users': sum(labels.values()),
        'missing_labels': len(candidates) - sum(labels.values()), 'labels': dict(labels),
        'valid': labels['0'] > 0 and labels['1'] > 0}
    write_report(destination, report)
    return report['valid']


def main() -> int:
    """Run the aggregate-only audit with safe errors and immutable reports."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-dir', type=Path, default=Path('data/raw'))
    parser.add_argument('--report', type=Path, default=Path('data/audit/history.json'),
                        help='Create once or verify identical JSON; never overwrite')
    parser.add_argument('--population-only', action='store_true',
                        help=('Audit original-only February subset target classes; '
                              'use a separate report path'))
    args = parser.parse_args()
    try:
        audit = audit_february_population if args.population_only else audit_history
        valid = audit(args.raw_dir, args.report)
    except (OSError, ValueError, UnicodeError, csv.Error):
        print('History audit blocked: verify sources, schema and report identity.',
              file=sys.stderr)
        return 2
    print('History audit valid.' if valid else 'History audit invalid: inspect aggregate report.')
    return 0 if valid else 1


if __name__ == '__main__':
    sys.exit(main())
