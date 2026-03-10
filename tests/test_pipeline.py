import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from delphi_to_rust_ai_orchestrator.pipeline import execute_pipeline


class TestPipeline(unittest.TestCase):
    def test_dry_run_does_not_write_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            legacy_dir = Path(tmp) / "legacy"
            legacy_dir.mkdir()
            # Create a legacy file so discovery returns at least one unit.
            (legacy_dir / "Example.pas").write_text("unit Example; implementation end.")

            with patch("delphi_to_rust_ai_orchestrator.pipeline.get_anthropic_client") as fake_client:
                fake_client.return_value = object()

                execute_pipeline(
                    legacy_dir=str(legacy_dir),
                    target_dir=str(Path(tmp) / "out"),
                    write_output=False,
                    rust_subdir="src",
                    tests_subdir="tests",
                    translate_func=lambda c, d, m, **kwargs: "// rust",
                    tests_func=lambda c, r, **kwargs: "// tests",
                )

            # Dry run should not create output directories.
            self.assertFalse((Path(tmp) / "out").exists())

    def test_writes_expected_structure(self):
        with tempfile.TemporaryDirectory() as tmp:
            legacy_dir = Path(tmp) / "legacy"
            legacy_dir.mkdir()
            (legacy_dir / "Example.pas").write_text("unit Example; implementation end.")

            out_dir = Path(tmp) / "out"

            with patch("delphi_to_rust_ai_orchestrator.pipeline.get_anthropic_client") as fake_client:
                fake_client.return_value = object()

                execute_pipeline(
                    legacy_dir=str(legacy_dir),
                    target_dir=str(out_dir),
                    write_output=True,
                    rust_subdir="src",
                    tests_subdir="tests",
                    translate_func=lambda c, d, m, **kwargs: "// rust code",
                    tests_func=lambda c, r, **kwargs: "// tests code",
                )

            # Ensure folders are created and files exist
            rust_file = out_dir / "src" / "Example.rs"
            test_file = out_dir / "tests" / "Example_golden_tests.rs"

            self.assertTrue(rust_file.exists())
            self.assertTrue(test_file.exists())
            self.assertEqual(rust_file.read_text(), "// rust code")
            self.assertEqual(test_file.read_text(), "// tests code")


if __name__ == "__main__":
    unittest.main()
