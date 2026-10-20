"""Compare LR and HGB using development only; freeze final policies without labels."""
import argparse
import csv
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from retention_lab.selection import compare_and_freeze


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for flag, default, help_text in (
            ('feature-dir', 'kkbox-features-v1', 'Frozen Phase 3 features and permitted labels'),
            ('eda-dir', 'kkbox-eda-v1', 'Frozen original-source provenance'),
            ('legacy-dir', 'kkbox-models-v1', 'Unchanged original LogisticRegression artifacts'),
            ('output-dir', 'kkbox-selection-v1', 'Private immutable comparison and final policies')):
        parser.add_argument('--' + flag, type=Path, default=Path('data/processed') / default,
                            help=help_text)
    parser.add_argument('--verify-real-population', action='store_true',
                        help='Require the original 523998/175651/174931 users')
    args = parser.parse_args()
    try:
        result = compare_and_freeze(args.feature_dir, args.eda_dir, args.legacy_dir,
                                    args.output_dir, args.verify_real_population)
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, csv.Error):
        print('Selection blocked: verify frozen provenance, schemas, original model and '
              'closed-test state. Existing artifacts were not overwritten.', file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
