import csv
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"


class CliSmokeTests(unittest.TestCase):
    def test_biz_only_end_to_end_without_upstream(self):
        with tempfile.TemporaryDirectory() as td:
            td_path = Path(td)
            input_path = td_path / "accounts.csv"
            output_dir = td_path / "output"
            with input_path.open("w", encoding="utf-8-sig", newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=["公众号名称", "分类", "biz"])
                writer.writeheader()
                writer.writerow({"公众号名称": "测试公众号A", "分类": "桌面 > 测试", "biz": "MzA1MjM0NTY3OA=="})
                writer.writerow({"公众号名称": "测试公众号B", "分类": "桌面 > 测试", "biz": "MzI5ODc2NTQzMg=="})

            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS / "generate_bookmarks.py"),
                    "--input",
                    str(input_path),
                    "--output-dir",
                    str(output_dir),
                ],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
            )
            self.assertEqual(proc.returncode, 0, msg=f"stdout={proc.stdout}\nstderr={proc.stderr}")

            for name in [
                "bookmarks.html",
                "wechat_accounts.csv",
                "unresolved.csv",
                "bookmark_review.csv",
                "redirect-map.json",
                "run_summary.json",
                "state.json",
            ]:
                self.assertTrue((output_dir / name).is_file(), msg=name)

            summary = json.loads((output_dir / "run_summary.json").read_text(encoding="utf-8"))
            self.assertEqual(summary["identity_resolved"], 2)
            self.assertEqual(summary["identity_unresolved"], 0)

            validate = subprocess.run(
                [sys.executable, str(SCRIPTS / "validate_output.py"), str(output_dir)],
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=30,
            )
            self.assertEqual(
                validate.returncode,
                0,
                msg=f"stdout={validate.stdout}\nstderr={validate.stderr}",
            )


if __name__ == "__main__":
    unittest.main()
