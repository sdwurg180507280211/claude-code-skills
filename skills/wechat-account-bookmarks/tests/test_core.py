import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

from bookmarks import build_homepage_url, render_bookmarks_html
from io_utils import InputEntry, load_entries, normalize_folder
from wechat_mp import parse_biz_from_html, parse_biz_from_url


class CoreTests(unittest.TestCase):
    def test_parse_biz_from_url(self):
        url = "https://mp.weixin.qq.com/s?__biz=MjM5NjM4MDAxMg%3D%3D&mid=1&idx=1&sn=x"
        self.assertEqual(parse_biz_from_url(url), "MjM5NjM4MDAxMg==")

    def test_parse_biz_from_html(self):
        self.assertEqual(parse_biz_from_html('var biz = "MzA123456789==";'), "MzA123456789==")

    def test_build_homepage_url(self):
        url = build_homepage_url("MjM5NjM4MDAxMg==")
        self.assertTrue(url.startswith("https://mp.weixin.qq.com/mp/profile_ext?"))
        self.assertIn("action=home", url)
        self.assertIn("scene=124", url)
        self.assertTrue(url.endswith("#wechat_redirect"))

    def test_folder_normalization(self):
        self.assertEqual(normalize_folder("桌面 > 财经新闻", "桌面"), ["财经新闻"])

    def test_bookmarks_html(self):
        entries = [
            InputEntry("财新", "桌面 > 财经新闻"),
            InputEntry("iNature", "桌面 > 科研学术"),
        ]
        result = {
            "财新": {"homepage_url": "https://example.com/caixin"},
            "iNature": {"homepage_url": "https://example.com/inature"},
        }
        html = render_bookmarks_html(entries, result)
        self.assertIn("微信公众号", html)
        self.assertIn("财经新闻", html)
        self.assertIn("财新", html)
        self.assertIn("https://example.com/caixin", html)

    def test_csv_input(self):
        with tempfile.TemporaryDirectory() as td:
            path = Path(td) / "accounts.csv"
            path.write_text("公众号名称,分类\n财新,桌面 > 财经新闻\n", encoding="utf-8-sig")
            entries, meta = load_entries(path)
            self.assertEqual(entries[0].name, "财新")
            self.assertEqual(meta["name_column"], "公众号名称")


if __name__ == "__main__":
    unittest.main()
