import tempfile
import unittest
from pathlib import Path
from scripts.create_skill import create

class GeneratorTests(unittest.TestCase):
    def test_create(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = create('excel-comparison', 'Compare two Excel files and report differences.', Path(tmp))
            self.assertTrue((path / 'SKILL.md').exists())
            self.assertIn('name: excel-comparison', (path / 'SKILL.md').read_text())
    def test_reject_unsafe_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                create('../bad', 'Unsafe', Path(tmp))
    def test_reject_duplicate(self):
        with tempfile.TemporaryDirectory() as tmp:
            create('sample', 'Example', Path(tmp))
            with self.assertRaises(FileExistsError):
                create('sample', 'Example', Path(tmp))
if __name__ == '__main__':
    unittest.main()
