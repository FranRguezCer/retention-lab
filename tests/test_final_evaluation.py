"""One-shot evaluator public CLI probes on synthetic outcomes only."""
import csv
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import unittest

import numpy as np
import test_train as training

ROOT = training.ROOT
sys.path.insert(0, str(ROOT / 'src'))


class FinalEvaluationTests(unittest.TestCase):
    def setUp(self):
        # Import first so missing functionality is observed as RED without side effects.
        from retention_lab import final_evaluation
        from retention_lab.selection import compare_and_freeze, SOURCES, RULE
        from retention_lab.data import fingerprint
        self.fixture = training.ModelTests()
        self.fixture.setUp()
        self.addCleanup(self.fixture.doCleanups)
        self.fixture.run_cli()
        self.features, self.eda = self.fixture.features, self.fixture.eda
        self.raw = self.fixture.fixture.raw
        self.frozen = self.features.parent / 'selected'
        self.output = self.features.parent / 'evaluation'
        compare_and_freeze(self.features, self.eda, self.fixture.output, self.frozen)
        self.repository = self.features.parent / 'repository'
        self.repository.mkdir()
        shutil.copytree(ROOT / 'src', self.repository / 'src', ignore=shutil.ignore_patterns('__pycache__'))
        (self.repository / 'scripts').mkdir()
        for name in ('select_kkbox_model.py', 'evaluate_kkbox.py'):
            shutil.copyfile(ROOT / 'scripts' / name, self.repository / 'scripts' / name)
        shutil.copyfile(ROOT / 'requirements.txt', self.repository / 'requirements.txt')
        anchor = self.repository / 'artifacts/model_freeze.json'
        anchor.parent.mkdir()
        manifest = json.loads((self.frozen / 'manifest.json').read_text())
        anchor.write_text(json.dumps({'version':1, 'manifest':fingerprint(self.frozen/'manifest.json'),
                                      'selected_model':manifest['selected_model'], 'rule':RULE}))
        def git(*args):
            return subprocess.check_output(['git','-C',str(self.repository),*args],stderr=subprocess.DEVNULL)
        git('init','-q'); git('add','.')
        git('-c','user.name=Synthetic Test','-c','user.email=test@example.invalid',
            'commit','-qm','test: freeze synthetic policies before outcomes')
        self.commit = git('rev-parse','HEAD').decode().strip()

    def cli(self, success=True, commit=None, output=None):
        result = subprocess.run([sys.executable, str(self.repository/'scripts/evaluate_kkbox.py'),
                                 '--frozen-dir',str(self.frozen), '--feature-dir',str(self.features),
                                 '--eda-dir',str(self.eda), '--labels',str(self.raw/'train.csv'),
                                 '--output-dir',str(output or self.output),
                                 '--freeze-commit', self.commit if commit is None else commit],
                                capture_output=True,text=True)
        self.assertEqual(result.returncode,0 if success else 2,result.stderr)
        self.assertNotIn('synthetic-',result.stdout+result.stderr)
        return result

    def test_one_pass_exact_join_real_curves_signs_and_cached_no_reopening(self):
        with (self.frozen/'final_keys.csv').open() as f:
            keys=[r['msno'] for r in csv.DictReader(f)]
        with (self.raw/'train.csv').open() as f:
            rows=list(csv.reader(f))
        original={r[0]:int(r[1]) for r in rows[1:] if r[0] in set(keys)}
        for row in rows[1:]:
            if row[0] not in set(keys):
                row[1]='not a label, "quoted"\nignored'
        with (self.raw/'train.csv').open('w',newline='') as f:
            csv.writer(f).writerows(rows)
        self.cli()
        result=json.loads((self.output/'results.json').read_text())
        self.assertEqual(result['positives'],sum(original.values()))
        with (self.frozen/'final_rankings.csv').open() as f:
            orders=list(csv.DictReader(f))
        for point in result['curve']:
            k=point['ml']['k']
            for policy in ('random','business','ml'):
                selected=[keys[int(r[policy])] for r in orders[:k]]
                name='random_permutation' if policy=='random' else policy
                self.assertEqual(point[name]['captured'],sum(original[u] for u in selected))
            if result['positives']:
                self.assertAlmostEqual(point['ml_minus_business_recall_pp'],
                                       100*(point['ml']['recall']-point['business']['recall']))
                self.assertAlmostEqual(point['ml_minus_random_expected_recall_pp'],
                                       100*(point['ml']['recall']-point['random_expected']['recall']))
        self.assertEqual(result['curve'][-1]['ml']['recall'],1.)
        text=(self.output/'results.json').read_text()
        self.assertTrue(all(key not in text for key in keys))
        before={p.name:p.read_bytes() for p in self.output.iterdir()}
        (self.raw/'train.csv').unlink()
        self.cli()  # Verified readback must not reopen or even require raw labels.
        self.assertEqual(before,{p.name:p.read_bytes() for p in self.output.iterdir()})
        self.cli(success=False,output=self.output.parent/'another-attempt')
        self.assertEqual(self.output.stat().st_mode & 0o077,0)

    def test_gate_blocks_before_label_open_and_then_tamper_blocks(self):
        (self.raw/'train.csv').unlink()
        self.cli(success=False,commit='0'*40)
        self.assertFalse((self.frozen/'evaluation_started.json').exists())
        path=self.frozen/'final_rankings.csv'
        path.write_bytes(path.read_bytes()+b'bad\n')
        self.cli(success=False)
        self.assertFalse((self.frozen/'evaluation_started.json').exists())

    def test_invalid_final_label_consumes_attempt_without_results_or_retry(self):
        from retention_lab.data import read_rows
        keys=set(r[0] for r in read_rows(self.frozen/'final_keys.csv',['msno']))
        with (self.raw/'train.csv').open() as f:
            rows=list(csv.reader(f))
        next(row for row in rows[1:] if row[0] in keys)[1]='invalid'
        with (self.raw/'train.csv').open('w',newline='') as f:
            csv.writer(f).writerows(rows)
        self.cli(success=False)
        self.assertTrue((self.frozen/'evaluation_started.json').exists())
        self.assertFalse((self.output/'manifest.json').exists())
        self.cli(success=False)

    def test_cached_artifact_corruption_is_not_a_new_evaluation(self):
        self.cli()
        path=self.output/'results.json'
        path.write_bytes(path.read_bytes()+b'corrupt')
        before={p.name:p.read_bytes() for p in self.output.iterdir()}
        self.cli(success=False)
        self.assertEqual(before,{p.name:p.read_bytes() for p in self.output.iterdir()})

    def test_plot_reproduces_from_cached_counts_without_outcomes(self):
        from retention_lab.final_evaluation import render_curve
        self.cli()
        result=json.loads((self.output/'results.json').read_text())
        with np.load(self.output/'curve_counts.npz',allow_pickle=False) as archive:
            counts={k:archive[k] for k in archive.files}
        other=self.output.parent/'reproduced.png'
        render_curve(counts,result['n'],result['positives'],other)
        self.assertEqual((self.output/'capacity_curve.png').read_bytes(),other.read_bytes())


    def test_duplicate_original_identifier_consumes_one_attempt(self):
        with (self.raw/'train.csv').open() as f:
            rows=list(csv.reader(f))
        rows.append(rows[1])
        with (self.raw/'train.csv').open('w',newline='') as f:
            csv.writer(f).writerows(rows)
        self.cli(success=False)
        self.assertTrue((self.frozen/'evaluation_started.json').exists())
        self.assertFalse((self.output/'manifest.json').exists())
        self.cli(success=False)

    def test_missing_original_identifier_consumes_one_attempt(self):
        with (self.raw/'train.csv').open() as f:
            rows=list(csv.reader(f))
        with (self.raw/'train.csv').open('w',newline='') as f:
            csv.writer(f).writerows(rows[:-1])
        self.cli(success=False)
        self.assertTrue((self.frozen/'evaluation_started.json').exists())
        self.assertFalse((self.output/'manifest.json').exists())
        self.cli(success=False)

    def test_simultaneous_starts_open_outcomes_only_once(self):
        counter=self.features.parent/'outcome-read-count.txt'
        wrapper='''
import pathlib, runpy, sys, time
sys.path.insert(0, sys.argv[1])
from retention_lab import final_evaluation
original = final_evaluation.final_outcomes
counter = pathlib.Path(sys.argv[2])
def counted(*args):
    with counter.open('a') as stream:
        stream.write('read\\n')
    time.sleep(.5)
    return original(*args)
final_evaluation.final_outcomes = counted
script = sys.argv[3]
sys.argv = sys.argv[3:]
runpy.run_path(script, run_name='__main__')
'''
        command=[sys.executable,'-c',wrapper,str(self.repository/'src'),str(counter),
                 str(self.repository/'scripts/evaluate_kkbox.py'),
                 '--frozen-dir',str(self.frozen),'--feature-dir',str(self.features),
                 '--eda-dir',str(self.eda),'--labels',str(self.raw/'train.csv'),
                 '--output-dir',str(self.output),'--freeze-commit',self.commit]
        children=[subprocess.Popen(command,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
                  for _ in range(2)]
        results=[(child.communicate(timeout=60),child.returncode) for child in children]
        self.assertIn(0,[r[1] for r in results],results)
        self.assertTrue(all(r[1] in (0,2) for r in results),results)
        self.assertEqual(counter.read_text().splitlines(),['read'])
        self.assertTrue((self.output/'manifest.json').exists())



class UndefinedFinalMetricsTests(unittest.TestCase):
    def test_zero_positive_curve_and_differences_are_explicitly_undefined(self):
        from retention_lab.final_evaluation import build_results
        result, _ = build_results(np.zeros(4, dtype=int),
                                  {p:[0,1,2,3] for p in ('random','business','ml')}, 'hgb')
        for row in result['curve']:
            self.assertIsNone(row['ml']['recall'])
            self.assertIsNone(row['ml']['lift'])
            self.assertIsNone(row['ml_minus_business_recall_pp'])
            self.assertIsNone(row['ml_minus_random_expected_recall_pp'])
