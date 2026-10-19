"""Execute the training-only notebook twice in fresh kernels; publish aggregates."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import sys
import tempfile

import nbformat
from nbclient import NotebookClient
from jupyter_client.kernelspec import KernelSpecManager

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from retention_lab.eda import load_training, summarize


def stable_outputs(notebook):
    """Compare aggregate text and image bytes, excluding transient metadata."""
    return [[{k: v for k, v in output.items() if k in ('output_type', 'text', 'data', 'name')}
             for output in cell.get('outputs', [])] for cell in notebook.cells]


def validate_public(notebook, identifiers):
    """Reject private identifiers, local absolute paths, or error outputs."""
    serialized = nbformat.writes(notebook)
    if any(user in serialized for user in identifiers):
        raise ValueError('Private identifier in notebook')
    if any(token in serialized for token in (str(ROOT), str(Path.home()), '/tmp/retention-')):
        raise ValueError('Private absolute path in notebook')
    for cell in notebook.cells:
        for output in cell.get('outputs', []):
            if output.output_type == 'error':
                raise ValueError('Notebook contains an error')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--check', action='store_true', help='Compare reruns with published notebook and aggregates without writing')
    args = parser.parse_args()
    path = ROOT / 'notebooks/01_eda.ipynb'
    original = nbformat.read(path, as_version=4)
    with tempfile.TemporaryDirectory(prefix='retention-notebook-') as temp:
        scratch = Path(temp)
        kernel = scratch / 'kernels' / 'eda-python312'
        kernel.mkdir(parents=True)
        (kernel / 'kernel.json').write_text(json.dumps({
            'argv': [sys.executable, '-m', 'ipykernel_launcher', '-f', '{connection_file}'],
            'display_name': 'Python 3.12 (EDA)', 'language': 'python'}))
        manager = KernelSpecManager(kernel_dirs=[str(scratch / 'kernels')])
        env = {**os.environ, 'MPLCONFIGDIR': str(scratch / 'mpl'),
               'IPYTHONDIR': str(scratch / 'ipython'), 'JUPYTER_RUNTIME_DIR': str(scratch / 'runtime'),
               'PYTHONDONTWRITEBYTECODE': '1', 'MPLBACKEND': 'module://matplotlib_inline.backend_inline'}
        runs = []
        for _ in range(2):
            notebook = copy.deepcopy(original)
            for cell in notebook.cells:
                if cell.cell_type == 'code':
                    cell.outputs = []
                    cell.execution_count = None
            client = NotebookClient(notebook, timeout=240, kernel_name='eda-python312',
                                    resources={'metadata': {'path': str(ROOT)}})
            client.create_kernel_manager().kernel_spec_manager = manager
            client.execute(env=env)
            runs.append(notebook)
        if stable_outputs(runs[0]) != stable_outputs(runs[1]):
            raise ValueError('Clean-kernel notebook outputs differ')
        import csv
        private = ROOT / 'data/processed/kkbox-eda-v1'
        with (private / 'assignments.csv').open() as stream:
            validate_public(runs[0], (r['msno'] for r in csv.DictReader(stream)))
        summary = summarize(load_training(private))
        payload = json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + '\n'
        aggregate = ROOT / 'artifacts/eda_summary.json'
        if args.check:
            if stable_outputs(original) != stable_outputs(runs[0]) or aggregate.read_text() != payload:
                raise ValueError('Published outputs differ from reconstruction')
        else:
            for cell in runs[0].cells:
                cell.metadata = {}
                for output in cell.get('outputs', []):
                    if 'data' in output:
                        output['metadata'] = {}
            runs[0].metadata = {'kernelspec': {'display_name': 'Python 3.12 (EDA)',
                                              'language': 'python', 'name': 'python3'}}
            nbformat.validate(runs[0])
            aggregate.parent.mkdir(exist_ok=True)
            aggregate.write_text(payload)
            nbformat.write(runs[0], path)
        print('Two clean kernels: identical aggregate text and figures; privacy checks passed.')
        print('Aggregate SHA-256:', hashlib.sha256(payload.encode()).hexdigest())


if __name__ == '__main__':
    main()
