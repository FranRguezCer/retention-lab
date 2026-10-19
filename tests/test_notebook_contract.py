"""Structural contract for the published training-only notebook."""
from pathlib import Path
import unittest

import nbformat


class NotebookContractTests(unittest.TestCase):
    def test_published_notebook_schema_and_training_only_input(self):
        path = Path(__file__).resolve().parents[1] / 'notebooks/01_eda.ipynb'
        notebook = nbformat.read(path, as_version=4)
        nbformat.validate(notebook)
        source = '\n'.join(c.source for c in notebook.cells if c.cell_type == 'code')
        self.assertIn('load_training', source)
        self.assertNotIn('train.csv', source)
        self.assertNotIn('assignments.csv', source)
        self.assertNotIn('partition', source)
        self.assertNotIn('data/raw', source)


if __name__ == '__main__':
    unittest.main()
