import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('preparation', ROOT / 'run.py')
prep = importlib.util.module_from_spec(spec)
spec.loader.exec_module(prep)


class PreparationTests(unittest.TestCase):
    def test_execution_refused(self):
        self.assertEqual(prep.main(['run']), 2)

    def test_review_config_preserves_route_and_thresholds(self):
        c = json.loads((ROOT / 'audit-config.json').read_text())
        self.assertEqual(prep.validate(c), [])
        c['B']['route_ned_m'][2][0] = 3
        self.assertTrue(prep.validate(c))

    def test_preservation_detects_tampering(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            p = root / 'console.log'
            p.write_text('evidence\n')
            m = prep.manifest(root)
            self.assertEqual(prep.verify(root, m), [])
            p.write_text('different\n')
            self.assertEqual(prep.verify(root, m), ['console.log'])

    def test_unsafe_manifest_paths_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            for rel in ['../outside', '/outside', 'C:\\outside', 'sub\\outside']:
                with self.assertRaises(ValueError):
                    prep.verify(Path(d), {rel: {'bytes': 1, 'sha256': 'x'}})

    def test_symlink_not_followed(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            (root / 'target').write_text('test')
            (root / 'link').symlink_to(root / 'target')
            with self.assertRaises(ValueError):
                prep.manifest(root)


if __name__ == '__main__':
    unittest.main()
