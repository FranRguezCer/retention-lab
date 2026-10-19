"""Stream two manually acquired KKBOX CSVs into a local aggregate audit."""
import argparse
import csv
from datetime import datetime
import hashlib
import json
from pathlib import Path
import sys

SCHEMAS = {
    'train_v2.csv': ['msno', 'is_churn'],
    'transactions_v2.csv': [
        'msno', 'payment_method_id', 'payment_plan_days', 'plan_list_price',
        'actual_amount_paid', 'is_auto_renew', 'transaction_date',
        'membership_expire_date', 'is_cancel'],
}
DATE_COLUMNS = ['transaction_date', 'membership_expire_date']


def fingerprint(path: Path) -> dict:
    """Hash source bytes with bounded memory, without modifying the source."""
    digest = hashlib.sha256()
    size = 0
    with path.open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            digest.update(chunk)
            size += len(chunk)
    return {'size_bytes': size, 'sha256': digest.hexdigest()}


def inspect_csv(path: Path, columns: list[str]) -> dict:
    """Validate fixed columns and collect counts without retaining identifiers."""
    result = {'columns': columns, 'rows': 0, 'missing': dict.fromkeys(columns, 0)}
    if 'is_churn' in columns:
        result['labels'] = {'0': 0, '1': 0, 'invalid': 0}
    else:
        result['dates'] = {
            col: {'invalid': 0, 'min': None, 'max': None} for col in DATE_COLUMNS}
    with path.open(encoding='utf-8-sig', newline='') as stream:
        reader = csv.reader(stream, strict=True)
        if next(reader, None) != columns:
            raise ValueError('Unexpected schema')
        for row in reader:
            if len(row) != len(columns):
                raise ValueError('Unexpected row width')
            result['rows'] += 1
            values = dict(zip(columns, row))
            for col, value in values.items():
                result['missing'][col] += int(not value.strip())
            if 'labels' in result:
                value = values['is_churn']
                result['labels'][value if value in ('0', '1') else 'invalid'] += 1
            else:
                for col, stats in result['dates'].items():
                    value = values[col]
                    try:
                        if len(value) != 8 or not value.isascii() or not value.isdigit():
                            raise ValueError('Invalid date shape')
                        datetime.strptime(value, '%Y%m%d')
                    except ValueError:
                        stats['invalid'] += 1
                    else:
                        stats['min'] = min(stats['min'] or value, value)
                        stats['max'] = max(stats['max'] or value, value)
    result['valid'] = result['rows'] > 0 and not any(result['missing'].values())
    result['valid'] &= not result.get('labels', {}).get('invalid', 0)
    result['valid'] &= not any(d['invalid'] for d in result.get('dates', {}).values())
    return result


def audit(raw_dir: Path, report_path: Path) -> bool:
    """Create once or verify an identical report; refuse changed evidence."""
    sources = [raw_dir / name for name in SCHEMAS]
    if any(report_path.resolve() == p.resolve() for p in sources):
        raise ValueError('Report must not be a source file')
    before = {p.name: fingerprint(p) for p in sources}
    report = {
        'audit_version': 1,
        'configuration': {'encoding': 'utf-8-sig', 'date_format': 'YYYYMMDD',
                          'schemas': SCHEMAS, 'binary_labels': ['0', '1']},
        'files': {},
    }
    for path in sources:
        report['files'][path.name] = {**before[path.name],
                                     **inspect_csv(path, SCHEMAS[path.name])}
    if before != {p.name: fingerprint(p) for p in sources}:
        raise ValueError('Source changed during audit')
    report['valid'] = all(item['valid'] for item in report['files'].values())
    payload = (json.dumps(report, indent=2, sort_keys=True) + '\n').encode('utf-8')
    if report_path.exists():
        if report_path.read_bytes() != payload:
            raise ValueError('Existing report differs; use a new report path')
    else:
        report_path.parent.mkdir(parents=True, exist_ok=True)
        with report_path.open('xb') as stream:
            stream.write(payload)
    return report['valid']


def main() -> int:
    """Expose the audit without printing source records or parser exceptions."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-dir', type=Path, default=Path('data/raw'),
                        help='Directory containing exactly named target CSVs (others ignored)')
    parser.add_argument('--report', type=Path, default=Path('data/audit/kkbox.json'),
                        help='Local JSON; existing content must match, never overwritten')
    args = parser.parse_args()
    try:
        valid = audit(args.raw_dir, args.report)
    except (OSError, ValueError, UnicodeError, csv.Error):
        print('Audit blocked: check files, schema, CSV structure and report identity. '
              'No existing report was overwritten.', file=sys.stderr)
        return 2
    print('Audit valid.' if valid else 'Audit invalid: inspect aggregate counts.')
    return 0 if valid else 1


if __name__ == '__main__':
    sys.exit(main())
