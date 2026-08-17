import sys
import unittest
from pathlib import Path
from unittest.mock import call, patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import batch_add_wechat as target


class AndroidShortcutCoreTests(unittest.TestCase):
    def test_parse_adb_devices_only_returns_authorized_devices(self):
        output = """List of devices attached\nAAA\tdevice product:test model:one\nBBB\toffline\nCCC\tunauthorized\nDDD\tdevice usb:1\n"""
        self.assertEqual(target.parse_adb_devices(output), ["AAA", "DDD"])

    def test_matches_search_short_and_long_names(self):
        self.assertTrue(target.matches_search("央视新闻 公众号", "央视新闻"))
        self.assertFalse(target.matches_search("央视网 公众号", "央视新闻"))
        self.assertTrue(target.matches_search("中国银行保险报电子报 小程序", "中国银行保险报电子报"))

    def test_matches_full_allows_spacing_and_hyphen_differences(self):
        self.assertTrue(target.matches_full("大众新闻大众日报", "大众新闻-大众日报"))
        self.assertFalse(target.matches_full("大众新闻", "大众新闻-大众日报"))

    def test_matches_confirm_rejects_short_shared_prefix(self):
        name = "中国银行保险报电子报"
        self.assertFalse(target.matches_confirm("中国银行保险报…", name))
        self.assertTrue(target.matches_confirm("中国银行保险报电…", name))

    def test_pick_candidates_prefers_public_account_over_mini_program(self):
        items = [
            {"x": 100, "y": 620, "w": 300, "h": 60, "text": "央视新闻"},
            {"x": 500, "y": 690, "w": 120, "h": 50, "text": "小程序"},
            {"x": 100, "y": 1100, "w": 300, "h": 60, "text": "央视新闻"},
            {"x": 500, "y": 1170, "w": 120, "h": 50, "text": "公众号"},
        ]
        cands = target.pick_candidates(items, "央视新闻")
        self.assertEqual(len(cands), 2)
        self.assertEqual(cands[0][1], "公众号")
        self.assertEqual(cands[1][1], "小程序")

    def test_top_activity_from_dumpsys(self):
        text = "topResumedActivity=ActivityRecord{abc u0 com.tencent.mm/.plugin.fts.ui.FTSMainUI t123}"
        self.assertEqual(
            target.top_activity_from_dumpsys(text),
            "com.tencent.mm/.plugin.fts.ui.FTSMainUI",
        )

    def test_run_batch_restores_original_ime(self):
        with (
            patch.object(target, "ensure_serial", return_value="device-1"),
            patch.object(target, "get_default_ime", return_value="com.example/.Ime"),
            patch.object(target, "set_ime", return_value=True) as set_ime,
            patch.object(target, "process", return_value=True),
        ):
            self.assertEqual(target.run_batch(["央视新闻"]), 0)
        self.assertEqual(
            set_ime.call_args_list,
            [call(target.ADB_KEYBOARD_IME), call("com.example/.Ime")],
        )

    def test_run_batch_restores_ime_even_when_processing_raises(self):
        with (
            patch.object(target, "ensure_serial", return_value="device-1"),
            patch.object(target, "get_default_ime", return_value="com.example/.Ime"),
            patch.object(target, "set_ime", return_value=True) as set_ime,
            patch.object(target, "process", side_effect=RuntimeError("boom")),
        ):
            self.assertEqual(target.run_batch(["央视新闻"]), 0)
        self.assertEqual(set_ime.call_args_list[-1], call("com.example/.Ime"))


if __name__ == "__main__":
    unittest.main()
