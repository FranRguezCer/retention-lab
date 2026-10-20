"""Train frozen Phase 4 strategies and scores; never accept final outcome inputs."""
import argparse
import csv
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from sklearn.exceptions import ConvergenceWarning
from retention_lab.train import MAX_ITER, SEED, train_and_score


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--feature-dir', type=Path, default=Path('data/processed/kkbox-features-v1'),
                        help='Verified frozen Phase 3 features, keys and permitted labels')
    parser.add_argument('--eda-dir', type=Path, default=Path('data/processed/kkbox-eda-v1'),
                        help='Frozen Phase 2 provenance and assignments; no raw outcomes')
    parser.add_argument('--output-dir', type=Path, default=Path('data/processed/kkbox-models-v1'),
                        help='Private owner-only create-or-compare model, scores and rankings')
    parser.add_argument('--seed', type=int, default=SEED,
                        help='Purpose-specific ranking seed and classifier random_state (default: 42)')
    parser.add_argument('--max-iter', type=int, default=MAX_ITER,
                        help='Logistic optimization limit; nonconvergence refuses publication (default: 1000)')
    parser.add_argument('--verify-real-population', action='store_true',
                        help='Require the approved 523998 / 175651 / 174931 frozen partition counts')
    args = parser.parse_args()
    try:
        result = train_and_score(args.feature_dir, args.eda_dir, args.output_dir,
                                 args.seed, args.max_iter, args.verify_real_population)
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, csv.Error, ConvergenceWarning):
        print('Training blocked: verify frozen input schemas, provenance, convergence and '
              'immutable output identity. Existing artifacts were not overwritten.', file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
