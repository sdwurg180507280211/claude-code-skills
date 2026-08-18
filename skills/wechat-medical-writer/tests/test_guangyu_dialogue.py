import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "enhance_guangyu_dialogue.py"
spec = importlib.util.spec_from_file_location("enhance_guangyu_dialogue", SCRIPT)
module = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(module)


SAMPLE_HTML = '''
<section data-container="intro" style="old">
  <p data-container="intro-label" style="old">导读</p>
  <p data-container="intro-content" style="old">访谈导语</p>
</section>
<section data-container="dialogue" style="old">
  <p data-container="dialogue-title" style="old">CIN2 管理新时代</p>
  <section data-container="dialogue-bubble" data-side="left" style="old">
    <p data-container="dialogue-speaker" style="old">光愈在线</p>
    <p data-container="dialogue-text" style="old">问题</p>
  </section>
  <section data-container="dialogue-bubble" data-side="right" style="old">
    <p data-container="dialogue-speaker" style="old">梁静教授</p>
    <p data-container="dialogue-text" style="old">回答</p>
  </section>
</section>
'''


class GuangyuDialogueTests(unittest.TestCase):
    def test_injects_avatar_rows_and_restyles_intro(self):
        result, missing = module.enhance_html(
            SAMPLE_HTML,
            {"光愈在线": "assets/logo.png", "梁静教授": "assets/liang.png"},
        )
        self.assertEqual(missing, [])
        self.assertEqual(result.count('data-guangyu="avatar"'), 2)
        self.assertIn('src="assets/logo.png"', result)
        self.assertIn('src="assets/liang.png"', result)
        self.assertIn('border:2px solid #F24D60', result)
        self.assertIn('background:#F2F2F2', result)
        self.assertIn('data-guangyu="dialogue-row" data-side="left"', result)
        self.assertIn('data-guangyu="dialogue-row" data-side="right"', result)

    def test_reports_missing_speaker_avatar(self):
        result, missing = module.enhance_html(
            SAMPLE_HTML,
            {"光愈在线": "assets/logo.png"},
        )
        self.assertEqual(missing, ["梁静教授"])
        self.assertIn('data-container="dialogue-bubble" data-side="right"', result)

    def test_custom_accent_is_applied(self):
        result, missing = module.enhance_html(
            SAMPLE_HTML,
            {"光愈在线": "logo.png", "梁静教授": "liang.png"},
            accent="#CC3355",
        )
        self.assertEqual(missing, [])
        self.assertIn('background:#CC3355', result)
        self.assertIn('border:2px solid #CC3355', result)


if __name__ == "__main__":
    unittest.main()
