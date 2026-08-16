import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import resolver
from bookmarks import build_homepage_url, render_bookmarks_html
from io_utils import InputEntry, identity_fingerprint, load_entries, normalize_folder
from resolver import parse_biz_from_url, resolve_entry
from upstream import _ensure_repo


class CoreTests(unittest.TestCase):
    def test_parse_biz_from_url(self):
        url = "https://mp.weixin.qq.com/s?__biz=MjM5NjM4MDAxMg%3D%3D&mid=1&idx=1&sn=x"
        self.assertEqual(parse_biz_from_url(url), "MjM5NjM4MDAxMg==")

    def test_build_homepage_url(self):
        url = build_homepage_url("MjM5NjM4MDAxMg==")
        self.assertTrue(url.startswith("https://mp.weixin.qq.com/mp/profile_ext?"))
        self.assertIn("action=home", url)
        self.assertIn("scene=124", url)
        self.assertTrue(url.endswith("#wechat_redirect"))

    def test_folder_normalization(self):
        self.assertEqual(normalize_folder("桌面 > 财经新闻", "桌面"), ["财经新闻"])

    def test_bookmarks_html_uses_resolved_target_url(self):
        entries = [
            InputEntry("财新", "桌面 > 财经新闻"),
            InputEntry("iNature", "桌面 > 科研学术"),
            InputEntry("待确认", "桌面 > 科研学术"),
        ]
        result = {
            "财新": {
                "identity_status": "resolved",
                "target_type": "homepage",
                "target_url": "https://example.com/caixin",
            },
            "iNature": {
                "identity_status": "resolved",
                "target_type": "article",
                "target_url": "https://example.com/inature-article",
            },
            "待确认": {
                "identity_status": "pending_review",
                "target_url": "https://example.com/should-not-appear",
            },
        }
        content = render_bookmarks_html(entries, result)
        self.assertIn("微信公众号", content)
        self.assertIn("财经新闻", content)
        self.assertIn("财新", content)
        self.assertIn("https://example.com/caixin", content)
        self.assertIn("https://example.com/inature-article", content)
        self.assertNotIn("should-not-appear", content)

    def test_csv_input_reads_url_and_biz(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "accounts.csv"
            path.write_text(
                "公众号名称,分类,URL,biz\n财新,桌面 > 财经新闻,https://mp.weixin.qq.com/s?__biz=abc,abc\n",
                encoding="utf-8-sig",
            )
            entries, meta = load_entries(path)
            self.assertEqual(entries[0].name, "财新")
            self.assertEqual(entries[0].url, "https://mp.weixin.qq.com/s?__biz=abc")
            self.assertEqual(entries[0].biz, "abc")
            self.assertEqual(meta["url_column"], "URL")
            self.assertEqual(meta["biz_column"], "biz")

    def test_xlsx_input_reads_url_and_biz(self):
        from openpyxl import Workbook

        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "accounts.xlsx"
            wb = Workbook()
            ws = wb.active
            ws.title = "公众号"
            ws.append(["快捷方式名称", "文件夹结构", "URL", "biz"])
            ws.append(["财新", "桌面 > 财经新闻", "https://mp.weixin.qq.com/s?__biz=abc", "abc"])
            wb.save(path)

            entries, meta = load_entries(path, sheet_name="公众号")
            self.assertEqual(entries[0].name, "财新")
            self.assertEqual(entries[0].folder, "桌面 > 财经新闻")
            self.assertEqual(entries[0].url, "https://mp.weixin.qq.com/s?__biz=abc")
            self.assertEqual(entries[0].biz, "abc")
            self.assertEqual(meta["sheet"], "公众号")

    def test_identity_fingerprint_ignores_folder_only_changes(self):
        one = [InputEntry("财新", "桌面 > A", "https://mp.weixin.qq.com/s?__biz=abc", "")]
        two = [InputEntry("财新", "桌面 > B", "https://mp.weixin.qq.com/s?__biz=abc", "")]
        self.assertEqual(identity_fingerprint(one), identity_fingerprint(two))

    def test_resolve_prefers_input_biz_without_upstream(self):
        with tempfile.TemporaryDirectory() as td:
            entry = InputEntry("财新", "财经", "", "abc==")
            result = resolve_entry(
                entry,
                upstream=None,
                adapter_script=SCRIPTS / "extract_identity.js",
                session_path=Path(td) / "session.json",
                work_dir=Path(td),
                validate=False,
            )
            self.assertEqual(result["identity_status"], "resolved")
            self.assertEqual(result["resolved_by"], "input_biz")
            self.assertEqual(result["biz"], "abc==")
            self.assertEqual(result["target_type"], "homepage")
            self.assertEqual(result["target_url"], result["homepage_url"])
            self.assertEqual(result["fallback_status"], "missing")
            self.assertEqual(result["current_name"], "")

    def test_input_url_without_upstream_requires_review(self):
        with tempfile.TemporaryDirectory() as td:
            url = "https://mp.weixin.qq.com/s?__biz=abc%3D%3D&mid=1&idx=1&sn=x"
            entry = InputEntry("财新", "财经", url, "")
            result = resolve_entry(
                entry,
                upstream=None,
                adapter_script=SCRIPTS / "extract_identity.js",
                session_path=Path(td) / "session.json",
                work_dir=Path(td),
                validate=False,
            )
            self.assertEqual(result["identity_status"], "pending_review")
            self.assertEqual(result["error_code"], "article_identity_unverified")
            self.assertEqual(result["fallback_article_url"], url)
            self.assertEqual(result["target_url"], "")

    def test_input_url_matching_account_is_resolved(self):
        with tempfile.TemporaryDirectory() as td:
            url = "https://mp.weixin.qq.com/s?__biz=abc%3D%3D&mid=1&idx=1&sn=x"
            entry = InputEntry("财新", "财经", url, "")
            extracted = {
                "ok": True,
                "account_name": "财新",
                "account_alias": "caixin",
                "account_id": "gh_test",
                "account_biz": "abc==",
                "msg_link": url,
                "msg_title": "测试文章",
            }
            with patch.object(resolver, "extract_with_upstream", return_value=extracted):
                result = resolve_entry(
                    entry,
                    upstream=object(),
                    adapter_script=SCRIPTS / "extract_identity.js",
                    session_path=Path(td) / "session.json",
                    work_dir=Path(td),
                    validate=False,
                )
            self.assertEqual(result["identity_status"], "resolved")
            self.assertEqual(result["current_name"], "财新")
            self.assertEqual(result["biz"], "abc==")
            self.assertEqual(result["fallback_status"], "present")
            self.assertEqual(result["target_type"], "homepage")

    def test_input_url_name_mismatch_goes_pending_review(self):
        with tempfile.TemporaryDirectory() as td:
            url = "https://mp.weixin.qq.com/s?__biz=abc%3D%3D&mid=1&idx=1&sn=x"
            entry = InputEntry("财新", "财经", url, "")
            extracted = {
                "ok": True,
                "account_name": "另一个公众号",
                "account_biz": "abc==",
                "msg_link": url,
            }
            with patch.object(resolver, "extract_with_upstream", return_value=extracted):
                result = resolve_entry(
                    entry,
                    upstream=object(),
                    adapter_script=SCRIPTS / "extract_identity.js",
                    session_path=Path(td) / "session.json",
                    work_dir=Path(td),
                    validate=False,
                )
            self.assertEqual(result["identity_status"], "pending_review")
            self.assertEqual(result["error_code"], "article_name_mismatch")
            self.assertEqual(result["current_name"], "另一个公众号")
            self.assertEqual(result["target_url"], "")

    def test_first_clone_materializes_worktree_even_when_head_matches_pin(self):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            source = root / "source"
            target = root / "target"
            source.mkdir()
            subprocess.run(["git", "init", "-q", str(source)], check=True)
            subprocess.run(["git", "-C", str(source), "config", "user.email", "test@example.com"], check=True)
            subprocess.run(["git", "-C", str(source), "config", "user.name", "Test"], check=True)
            marker = source / "scripts" / "marker.txt"
            marker.parent.mkdir()
            marker.write_text("ok", encoding="utf-8")
            subprocess.run(["git", "-C", str(source), "add", "."], check=True)
            subprocess.run(["git", "-C", str(source), "commit", "-qm", "init"], check=True)
            commit = subprocess.check_output(
                ["git", "-C", str(source), "rev-parse", "HEAD"], text=True
            ).strip()

            _ensure_repo(target, str(source), commit)
            self.assertTrue((target / "scripts" / "marker.txt").is_file())
            checked_out = subprocess.check_output(
                ["git", "-C", str(target), "rev-parse", "HEAD"], text=True
            ).strip()
            self.assertEqual(checked_out, commit)


if __name__ == "__main__":
    unittest.main()
