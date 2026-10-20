"""One final evaluation after explicit committed freeze; later calls read verified cache only."""
import argparse
import csv
import json
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from retention_lab.final_evaluation import evaluate_once


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--freeze-commit', required=True, help='Full ancestor SHA of pre-test freeze commit')
    for name, default, help_text in (
            ('frozen-dir','data/processed/kkbox-selection-v1','Committed, relationship-verified model freeze'),
            ('feature-dir','data/processed/kkbox-features-v1','Unchanged Phase3 artifacts'),
            ('eda-dir','data/processed/kkbox-eda-v1','Unchanged original-source provenance'),
            ('labels','data/raw/train.csv','Original labels; only final keys interpreted, AFTER the gate'),
            ('output-dir','data/processed/kkbox-evaluation-v1','PRIVATE output; no automatic public export')):
        parser.add_argument('--' + name, type=Path, default=Path(default), help=help_text)
    parser.add_argument('--verify-real-population', action='store_true',
                        help='Require exactly 174931 final users')
    args = parser.parse_args()
    try:
        result = evaluate_once(args.frozen_dir, args.feature_dir, args.eda_dir, args.labels,
                               args.output_dir, args.freeze_commit, args.verify_real_population)
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, csv.Error,
            subprocess.CalledProcessError):
        print('Evaluation blocked: check committed freeze, exact artifact identity and one-shot state. '
              'A consumed or interrupted attempt must not be retried with labels.', file=sys.stderr)
        return 2
    print(json.dumps({k: result[k] for k in ('selected_model', 'n', 'positives', 'table')},
                     sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
