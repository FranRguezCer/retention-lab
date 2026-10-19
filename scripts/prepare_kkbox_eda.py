"""Freeze original February partitions, then prepare training-only EDA inputs."""
import argparse
import csv
import json
from pathlib import Path
import sqlite3
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from retention_lab.eda_prepare import prepare


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-dir', type=Path, default=Path('data/raw'),
                        help='Original transactions.csv and train.csv; v2 files ignored')
    parser.add_argument('--output-dir', type=Path, default=Path('data/processed/kkbox-eda-v1'),
                        help='Private create-once artifacts; changed evidence is refused')
    parser.add_argument('--verify-real-population', action='store_true',
                        help='Require 874581 candidates and 874580 labeled identifiers')
    args = parser.parse_args()
    try:
        population = prepare(args.raw_dir, args.output_dir,
                             (874581, 874580) if args.verify_real_population else None)
    except (OSError, ValueError, UnicodeError, csv.Error, sqlite3.Error):
        print('Preparation blocked: check sources, schemas and immutable artifact identity. '
              'Existing artifacts were not overwritten.', file=sys.stderr)
        return 2
    print(json.dumps(population, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
