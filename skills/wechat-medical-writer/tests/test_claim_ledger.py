from __future__ import annotations

import importlib.util
import sys
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_claim_ledger.py"
spec = importlib.util.spec_from_file_location("validate_claim_ledger", SCRIPT)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


class ClaimLedgerTests(unittest.TestCase):
    def valid_claim(self) -> dict:
        return {
            "claim_id": "C001",
            "claim_text": "示例医学结论",
            "claim_type": "efficacy",
            "source_type": "external_primary",
            "source_ref": "Example Trial",
            "source_location": "p.10",
            "evidence_level": "RCT",
            "verification_status": "verified",
            "public_use_status": "ready",
            "notes": "",
        }

    def test_valid_claim_passes(self):
        self.assertEqual(mod.validate_claims([self.valid_claim()]), [])

    def test_duplicate_claim_id_is_rejected(self):
        claim = self.valid_claim()
        errors = mod.validate_claims([claim, dict(claim)])
        self.assertTrue(any("claim_id 重复" in error for error in errors))

    def test_model_inference_cannot_be_ready(self):
        claim = self.valid_claim()
        claim["source_type"] = "model_inference"
        claim["source_ref"] = ""
        errors = mod.validate_claims([claim])
        self.assertTrue(any("model_inference 不能直接标记为 ready" in error for error in errors))

    def test_unverified_claim_cannot_be_ready(self):
        claim = self.valid_claim()
        claim["verification_status"] = "not_checked"
        errors = mod.validate_claims([claim])
        self.assertTrue(any("public_use_status=ready" in error for error in errors))

    def test_non_model_source_requires_reference(self):
        claim = self.valid_claim()
        claim["source_ref"] = ""
        errors = mod.validate_claims([claim])
        self.assertTrue(any("必须填写 source_ref" in error for error in errors))


if __name__ == "__main__":
    unittest.main()
