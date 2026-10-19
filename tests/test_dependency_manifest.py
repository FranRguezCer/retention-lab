"""Keep direct imports, pinned versions and reproduction entry points aligned."""
import ast
import json
from pathlib import Path
import re
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]


def pins(path: Path) -> dict[str, str]:
    """Read exact package pins without requiring another dependency manager."""
    result = {}
    for line in path.read_text().splitlines():
        match = re.fullmatch(r'([A-Za-z0-9_.-]+)==([^\s;]+)', line.strip())
        if match:
            name, version = match.groups()
            result[re.sub(r'[-_.]+', '-', name).lower()] = version
    return result


class DependencyManifestTests(unittest.TestCase):
    def test_runtime_imports_are_declared_directly_and_locked(self):
        direct = pins(ROOT / 'requirements-eda.txt')
        locked = pins(ROOT / 'requirements-eda.lock')
        sources = list((ROOT / 'scripts').glob('*.py'))
        sources += list((ROOT / 'src').rglob('*.py'))
        sources += list((ROOT / 'tests').glob('*.py'))
        local = {p.stem for p in sources} | {'retention_lab'}
        texts = [p.read_text() for p in sources]
        notebook = json.loads((ROOT / 'notebooks/01_eda.ipynb').read_text())
        texts += [''.join(c['source']) for c in notebook['cells']
                  if c['cell_type'] == 'code']
        imported = set()
        for text in texts:
            for node in ast.walk(ast.parse(text)):
                if isinstance(node, ast.Import):
                    imported.update(a.name.split('.')[0] for a in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module.split('.')[0])
        external = imported - sys.stdlib_module_names - local
        # Kernel launcher and matplotlib backend are selected by string at runtime.
        external |= {'ipykernel', 'matplotlib_inline'}
        expected = {re.sub(r'[-_.]+', '-', name).lower() for name in external}
        self.assertTrue(expected <= direct.keys(),
                        f'Undeclared direct imports: {expected - direct.keys()}')
        for name, version in direct.items():
            self.assertEqual(locked.get(name), version, name)

    def test_direct_install_uses_the_verified_constraints(self):
        lines = (ROOT / 'requirements-eda.txt').read_text().splitlines()
        self.assertIn('-c requirements-eda.lock', lines)

    def test_readme_points_to_reproduction_and_current_results(self):
        readme = (ROOT / 'README.md').read_text()
        for target in ('docs/methodology.md', 'requirements-eda.lock',
                       'notebooks/01_eda.ipynb', 'PROGRESS.md'):
            self.assertIn(target, readme)
            self.assertTrue((ROOT / target).is_file())


if __name__ == '__main__':
    unittest.main()
