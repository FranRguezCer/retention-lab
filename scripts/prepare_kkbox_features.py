"""Prepare seven cutoff-safe features; keep validation labels separate and final unlabeled."""
import argparse
import csv
import json
from pathlib import Path
import sqlite3
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from retention_lab.features import prepare_features


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--raw-dir', type=Path, default=Path('data/raw'),
                        help='Original transactions.csv and train.csv only; never v2')
    parser.add_argument('--eda-dir', type=Path, default=Path('data/processed/kkbox-eda-v1'),
                        help='Verified immutable Phase 2 assignments, manifest and training artifacts')
    parser.add_argument('--output-dir', type=Path, default=Path('data/processed/kkbox-features-v1'),
                        help='Private create-or-compare feature tables and integrity manifest')
    parser.add_argument('--verify-real-population', action='store_true',
                        help='Require the exact approved candidate, labeled and three partition counts')
    args = parser.parse_args()
    try:
        population = prepare_features(args.raw_dir, args.eda_dir, args.output_dir,
                                      args.verify_real_population)
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, csv.Error, sqlite3.Error):
        print('Feature preparation blocked: check original sources, frozen EDA and '
              'immutable artifact identity. Existing artifacts were not overwritten.', file=sys.stderr)
        return 2
    print(json.dumps(population, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
