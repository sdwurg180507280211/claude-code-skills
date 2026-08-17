from __future__ import annotations

import csv
import importlib.util
import plistlib
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "generate_webclips.py"
spec = importlib.util.spec_from_file_location("generate_webclips", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules["generate_webclips"] = mod
spec.loader.exec_module(mod)


class WebClipGeneratorTests(unittest.TestCase):
    def test_wechat_accounts_csv_uses_original_name_when_current_name_is_blank(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "wechat_accounts.csv"
            with path.open("w", encoding="utf-8-sig", newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=["original_name", "current_name", "target_url"])
                writer.writeheader()
                writer.writerow(
                    {
                        "original_name": "证券时报",
                        "current_name": "",
                        "target_url": "https://mp.weixin.qq.com/s/example",
                    }
                )
            entries, skipped = mod.collect_entries(path, None, None, None, None)
            self.assertEqual([e.name for e in entries], ["证券时报"])
            self.assertEqual(skipped, [])

    def test_invalid_and_duplicate_rows_are_skipped(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "input.csv"
            with path.open("w", encoding="utf-8-sig", newline="") as fh:
                writer = csv.DictWriter(fh, fieldnames=["公众号名称", "target_url"])
                writer.writeheader()
                writer.writerow({"公众号名称": "量子位", "target_url": "https://mp.weixin.qq.com/s/a"})
                writer.writerow({"公众号名称": "量子位", "target_url": "https://mp.weixin.qq.com/s/b"})
                writer.writerow({"公众号名称": "无效", "target_url": "javascript:alert(1)"})
            entries, skipped = mod.collect_entries(path, None, None, None, None)
            self.assertEqual(len(entries), 1)
            self.assertEqual(entries[0].url, "https://mp.weixin.qq.com/s/a")
            self.assertEqual([row["reason"] for row in skipped], ["duplicate_name", "missing_or_invalid_url"])

    def test_profile_contains_multiple_webclip_payloads(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            entries = [
                mod.WebClipEntry("量子位", "https://mp.weixin.qq.com/s/a"),
                mod.WebClipEntry("财新", "https://mp.weixin.qq.com/s/b"),
            ]
            profile = mod.build_profile(
                entries,
                input_path=base / "input.csv",
                profile_name="微信公众号快捷方式",
                profile_identifier="com.example.wechat",
                organization="tests",
                fullscreen=False,
                removable=True,
            )
            self.assertEqual(profile["PayloadType"], "Configuration")
            self.assertEqual(len(profile["PayloadContent"]), 2)
            first = profile["PayloadContent"][0]
            self.assertEqual(first["PayloadType"], "com.apple.webClip.managed")
            self.assertEqual(first["Label"], "量子位")
            self.assertTrue(first["IsRemovable"])
            self.assertFalse(first["FullScreen"])
            encoded = plistlib.dumps(profile, fmt=plistlib.FMT_XML)
            decoded = plistlib.loads(encoded)
            self.assertEqual(decoded["PayloadContent"][1]["URL"], "https://mp.weixin.qq.com/s/b")

    def test_png_icon_is_embedded(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            icon = base / "icon.png"
            icon.write_bytes(mod.PNG_SIGNATURE + b"fake-png-body")
            entry = mod.WebClipEntry("测试", "https://example.com", "icon.png")
            payload = mod.build_webclip_payload(
                entry,
                profile_identifier="com.example.wechat",
                input_path=base / "input.csv",
                fullscreen=True,
                removable=False,
            )
            self.assertEqual(payload["Icon"], icon.read_bytes())
            self.assertTrue(payload["FullScreen"])
            self.assertFalse(payload["IsRemovable"])


if __name__ == "__main__":
    unittest.main()
