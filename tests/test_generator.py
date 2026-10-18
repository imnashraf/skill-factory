import tempfile
import unittest
from pathlib import Path
from scripts.create_skill import create
from skillfactory.core import generate_skill
from skillfactory.manifest import verify_manifest
from skillfactory.spec import SkillSpec


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

    def test_manifest_generation_and_integrity(self):
        """AC1.06: Verify .skillfactory/manifest.json accurately records SHA-256 hashes."""
        with tempfile.TemporaryDirectory() as tmp:
            spec = SkillSpec(
                name="manifest-skill",
                description="Verifying manifest generation and SHA-256 integrity.",
                template_family="python-script",
            )
            res = generate_skill(spec, Path(tmp))
            manifest_file = res.target_path / ".skillfactory" / "manifest.json"
            self.assertTrue(manifest_file.exists())

            # Verify manifest matches files
            valid, discrepancies = verify_manifest(res.target_path)
            self.assertTrue(valid, f"Discrepancies found: {discrepancies}")

            # Tamper with a file and verify discrepancy is detected
            script_file = res.target_path / "scripts" / "main.py"
            script_file.write_text("# Tampered content\n", encoding="utf-8")
            valid2, discrepancies2 = verify_manifest(res.target_path)
            self.assertFalse(valid2)
            self.assertTrue(any("File content modified" in d for d in discrepancies2))

    def test_template_rendering_artifacts(self):
        """AC1.05: Verify all expected artifacts are present in output."""
        with tempfile.TemporaryDirectory() as tmp:
            # 1. python-script
            spec_py = SkillSpec(name="script-artifacts", description="Artifact test", template_family="python-script")
            res_py = generate_skill(spec_py, Path(tmp))
            self.assertTrue((res_py.target_path / "SKILL.md").exists())
            self.assertTrue((res_py.target_path / "README.md").exists())
            self.assertTrue((res_py.target_path / "scripts" / "main.py").exists())
            self.assertTrue((res_py.target_path / "tests" / "test_placeholder.py").exists())
            self.assertTrue((res_py.target_path / "references" / "guide.md").exists())

            # 2. instructions-only
            spec_inst = SkillSpec(name="inst-artifacts", description="Artifact test", template_family="instructions-only")
            res_inst = generate_skill(spec_inst, Path(tmp))
            self.assertTrue((res_inst.target_path / "SKILL.md").exists())
            self.assertTrue((res_inst.target_path / "README.md").exists())
            self.assertTrue((res_inst.target_path / "references" / "guide.md").exists())
            self.assertTrue((res_inst.target_path / "examples" / "example.md").exists())


if __name__ == '__main__':
    unittest.main()
