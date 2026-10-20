"""Publish a verified post-hoc LR comparison from private v1 cached evidence only.

Never trains, scores, reselects, runs the original evaluator or opens raw CSVs.
Existing outputs must match exactly; originals and the consumed marker are retained.
"""
import argparse
import csv
from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from retention_lab.data import publish_private, write_json
from retention_lab.posthoc import comparison_markdown, extend_from_cache, render_comparison


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    for name, default, help_text in (
            ('legacy-dir', 'data/processed/kkbox-models-v1', 'Original frozen LR artifacts'),
            ('frozen-dir', 'data/processed/kkbox-selection-v1', 'Validation-selected HGB freeze'),
            ('evaluation-dir', 'data/processed/kkbox-evaluation-v1', 'Consumed original evaluation cache'),
            ('output-dir', 'artifacts', 'Only aggregate v2 JSON, table and PNG are exported')):
        parser.add_argument('--' + name, type=Path, default=Path(default), help=help_text)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    try:
        inputs = [p.resolve() for p in (args.legacy_dir, args.frozen_dir, args.evaluation_dir)]
        output = args.output_dir.resolve()
        if any(output == p or output in p.parents or p in output.parents for p in inputs):
            raise ValueError('Output overlaps private evidence')
        result, counts = extend_from_cache(
            args.legacy_dir, args.frozen_dir, args.evaluation_dir, root,
            '471525b34afdef2783350a734c4c2cfdd8366749',
            '7f21d9bb615ca5834e92fdc3fdf8f0928a62b7e8',
            'ec3e58ebf8f0312ab353ab1f854ba058d7c9d669', (174931, 9527))
        with tempfile.TemporaryDirectory(prefix='retention-posthoc-') as temporary:
            scratch = Path(temporary)
            write_json(scratch / 'capacity_comparison_v2.json', result)
            (scratch / 'capacity_comparison_v2.md').write_text(comparison_markdown(result))
            render_comparison(counts, result['n'], result['positives'],
                              scratch / 'capacity_comparison_v2.png')
            # Validate ALL conflicts before creating any output; never overwrite.
            from retention_lab.data import fingerprint
            for candidate in scratch.iterdir():
                target = args.output_dir / candidate.name
                if target.exists() and fingerprint(target) != fingerprint(candidate):
                    raise ValueError('Existing v2 output differs; preserve it')
            args.output_dir.mkdir(parents=True, exist_ok=True)
            for candidate in scratch.iterdir():
                publish_private(args.output_dir / candidate.name, candidate)
    except (OSError, ValueError, KeyError, TypeError, UnicodeError, csv.Error,
            subprocess.CalledProcessError):
        print('Post-hoc extension blocked: historical evidence, population or destination differs. '
              'Do not reopen raw labels, retrain or replace original evidence.', file=sys.stderr)
        return 2
    print('Verified descriptive v2 comparison exported; HGB remains selected. '
          'No raw CSV, training, scoring or model selection executed.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
