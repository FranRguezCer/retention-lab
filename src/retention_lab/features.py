"""Seven deterministic predictors; no fitting or final-outcome interpretation."""
from contextlib import ExitStack
import csv
import hashlib
import json
from pathlib import Path
import tempfile

from retention_lab.data import (
    CUTOFF, SALT, calendar, fingerprint, prepared_events, publish_private,
    read_rows, split_user, summarize_history, write_json,
)
from retention_lab.eda_prepare import TRAIN_COLUMNS

FEATURE_COLUMNS = ['auto_renew', 'observed_history_days', 'january_transactions',
                   'distinct_transactions', 'latest_plan_days', 'latest_amount',
                   'auto_on_to_off']
PARTITIONS = ('train', 'validation', 'final')
FILES = [f'{p}_{kind}.csv' for p in PARTITIONS for kind in ('keys', 'features')]
FILES += ['train_labels.csv', 'validation_labels.csv']
EXPECTED = {'train': 523998, 'validation': 175651, 'final': 174931}


def permitted_labels(raw: Path, assignments: Path, destination: Path) -> None:
    """Extract train/validation only after frozen assignment lookup.

    CSV parsing transports the final field; no branch evaluates its value.
    All label identifiers are checked, without hashing any final outcome bytes.
    """
    selected = {}
    for user, digest, bucket, partition in read_rows(
            assignments, ['msno', 'digest', 'bucket', 'partition']):
        if (digest, int(bucket), partition) != split_user(user) or user in selected:
            raise ValueError('Invalid frozen assignment')
        selected[user] = partition
    values = {'train': {}, 'validation': {}}
    ids = set()
    for user, value in read_rows(raw / 'train.csv', ['msno', 'is_churn']):
        if user in ids:
            raise ValueError('Duplicate label identifier')
        ids.add(user)
        partition = selected.get(user)
        if partition in values:
            if value not in ('0', '1'):
                raise ValueError('Invalid permitted label')
            values[partition][user] = value
    digest = hashlib.sha256()
    for user in sorted(ids):
        digest.update((json.dumps(user) + '\n').encode())
    manifest = json.loads((assignments.parent / 'manifest.json').read_text())
    if digest.hexdigest() != manifest['sources']['train.csv']['sorted_identifier_sha256']:
        raise ValueError('Label identifiers changed')
    if not set(selected).issubset(ids):
        raise ValueError('Missing assigned identifier')
    for partition, labels in values.items():
        with (destination / f'{partition}_labels.csv').open('w', newline='') as stream:
            writer = csv.writer(stream)
            writer.writerow(['msno', 'is_churn'])
            writer.writerows(sorted(labels.items()))


def validate_tables(directory: Path, eda: Path) -> None:
    """Check complete keys, schema, row alignment and exact training EDA parity."""
    expected = {p: [] for p in PARTITIONS}
    for user, digest, bucket, partition in read_rows(
            eda / 'assignments.csv', ['msno', 'digest', 'bucket', 'partition']):
        if (digest, int(bucket), partition) != split_user(user):
            raise ValueError('Invalid assignment')
        expected[partition].append(user)
    for partition in PARTITIONS:
        keys = [r[0] for r in read_rows(directory / f'{partition}_keys.csv', ['msno'])]
        if keys != expected[partition] or len(set(keys)) != len(keys):
            raise ValueError('Feature keys differ')
        rows = read_rows(directory / f'{partition}_features.csv', FEATURE_COLUMNS)
        count = 0
        for row in rows:
            # The first predictor is required; missing optional numerics are empty.
            if row[0] not in ('0', '1'):
                raise ValueError('Invalid renewal category')
            for value in row[1:]:
                if value:
                    int(value)
            count += 1
        if count != len(keys):
            raise ValueError('Feature coverage differs')
    training = iter(read_rows(eda / 'training.csv', TRAIN_COLUMNS))
    features = iter(read_rows(directory / 'train_features.csv', FEATURE_COLUMNS))
    labels = iter(read_rows(directory / 'train_labels.csv', ['msno', 'is_churn']))
    for row in training:
        original = dict(zip(TRAIN_COLUMNS, row))
        if next(features, None) != [original[c] for c in FEATURE_COLUMNS]:
            raise ValueError('Training features differ from EDA')
        if next(labels, None) != [original['msno'], original['is_churn']]:
            raise ValueError('Training labels differ from EDA')
    if next(features, None) is not None or next(labels, None) is not None:
        raise ValueError('Extra training records')
    validation = [r[0] for r in read_rows(directory / 'validation_labels.csv', ['msno', 'is_churn'])]
    if validation != expected['validation']:
        raise ValueError('Validation label coverage differs')


def prepare_features(raw: Path, eda: Path, output: Path, verify_real: bool = False) -> dict:
    """Build once, or verify a source-bound cache without rescanning all events."""
    roots = [p.resolve() for p in (raw, eda, output)]
    if any(a == b or a in b.parents or b in a.parents
           for i, a in enumerate(roots) for b in roots[i + 1:]):
        raise ValueError('Input/output directories overlap')
    if output.exists() and output.stat().st_mode & 0o077:
        raise ValueError('Feature directory must be owner-only')
    manifest = json.loads((eda / 'manifest.json').read_text())
    if manifest['configuration']['cutoff'] != CUTOFF or manifest['configuration']['salt'] != SALT:
        raise ValueError('Unsupported frozen configuration')
    if fingerprint(raw / 'transactions.csv') != manifest['sources']['transactions.csv']:
        raise ValueError('Original transaction source differs')
    if fingerprint(eda / 'assignments.csv') != manifest['assignments']:
        raise ValueError('Frozen assignments differ')
    quality = json.loads((eda / 'quality.json').read_text())
    if fingerprint(eda / 'training.csv') != quality['training_artifact']:
        raise ValueError('Frozen EDA training differs')
    population = manifest['population']
    if verify_real and (population['candidates'], population['labeled'],
                        population['unlabeled'], population['partitions']) != (874581, 874580, 1, EXPECTED):
        raise ValueError('Unexpected real population')
    provenance = {'version': 1, 'feature_columns': FEATURE_COLUMNS,
                  'eda': {n: fingerprint(eda / n) for n in
                          ('manifest.json', 'assignments.csv', 'training.csv', 'quality.json')},
                  'population': population, 'cutoff': CUTOFF,
                  'final_outcomes': 'never evaluated or exported'}
    with tempfile.TemporaryDirectory(prefix='retention-features-') as directory:
        scratch = Path(directory)
        permitted_labels(raw, eda / 'assignments.csv', scratch)
        if (output / 'manifest.json').exists():
            existing = json.loads((output / 'manifest.json').read_text())
            if {k: v for k, v in existing.items() if k != 'files'} != provenance:
                raise ValueError('Cached provenance differs')
            if set(existing['files']) != set(FILES):
                raise ValueError('Cached schema differs')
            for name in FILES:
                if fingerprint(output / name) != existing['files'][name]:
                    raise ValueError('Cached artifact differs')
            for name in ('train_labels.csv', 'validation_labels.csv'):
                if fingerprint(scratch / name) != existing['files'][name]:
                    raise ValueError('Permitted labels changed')
            validate_tables(output, eda)
            return population
        with prepared_events(raw, scratch / 'frozen') as (db, _, rebuilt_population, rebuilt):
            if rebuilt != manifest or rebuilt_population != population:
                raise ValueError('Shared preparation differs from frozen EDA')
            changes = summarize_history(db, 'assignment')
            query = ('SELECT l.msno,a.partition,l.is_auto_renew,h.first_day,h.january,'
                     'h.distinct_transactions,l.payment_plan_days,l.actual_amount_paid '
                     'FROM latest l JOIN assignment a USING(msno) JOIN history h USING(msno) '
                     'ORDER BY l.msno')
            with ExitStack() as stack:
                writers = {}
                for partition in PARTITIONS:
                    writers[partition] = []
                    for kind, columns in (('keys', ['msno']), ('features', FEATURE_COLUMNS)):
                        stream = stack.enter_context((scratch / f'{partition}_{kind}.csv').open('w', newline=''))
                        writer = csv.writer(stream)
                        writer.writerow(columns)
                        writers[partition].append(writer)
                for user, partition, auto, first, jan, count, days, amount in db.execute(query):
                    keys, features = writers[partition]
                    keys.writerow([user])
                    features.writerow([auto, (calendar(CUTOFF) - calendar(first)).days,
                                       jan, count, days, amount, changes[user][0]])
        validate_tables(scratch, eda)
        provenance['files'] = {n: fingerprint(scratch / n) for n in FILES}
        write_json(scratch / 'manifest.json', provenance)
        # Preflight every conflict before publishing any new file; manifest last.
        for name in FILES + ['manifest.json']:
            path = output / name
            if path.exists() and fingerprint(path) != fingerprint(scratch / name):
                raise ValueError('Existing feature artifact differs')
        output.mkdir(mode=0o700, parents=True, exist_ok=True)
        for name in FILES + ['manifest.json']:
            publish_private(output / name, scratch / name)
    return population
