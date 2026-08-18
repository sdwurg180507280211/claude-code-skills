#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REQUIRED_FIELDS = [
    "claim_id",
    "claim_text",
    "claim_type",
    "source_type",
    "source_ref",
    "source_location",
    "evidence_level",
    "verification_status",
    "public_use_status",
    "notes",
]

CLAIM_TYPES = {
    "indication",
    "contraindication",
    "dosage_or_procedure",
    "efficacy",
    "safety",
    "prognosis",
    "fertility",
    "mechanism",
    "guideline_recommendation",
    "regulatory_status",
    "comparative_claim",
    "background_fact",
}

SOURCE_TYPES = {
    "user_source",
    "external_primary",
    "external_secondary",
    "model_inference",
}

VERIFICATION_STATUSES = {
    "source_only",
    "verified",
    "conflicting",
    "insufficient",
    "not_checked",
}

PUBLIC_USE_STATUSES = {
    "ready",
    "medical_review",
    "compliance_review",
    "hold",
}


def load_claims(path: Path) -> list[dict]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(raw, list):
        claims = raw
    elif isinstance(raw, dict) and isinstance(raw.get("claims"), list):
        claims = raw["claims"]
    else:
        raise ValueError("Claim Ledger 必须是 JSON 数组，或包含 claims 数组的 JSON 对象")
    if not all(isinstance(item, dict) for item in claims):
        raise ValueError("claims 中每一项必须是 JSON 对象")
    return claims


def validate_claims(claims: list[dict]) -> list[str]:
    errors: list[str] = []
    seen_ids: set[str] = set()
    for index, claim in enumerate(claims, start=1):
        prefix = f"claim[{index}]"
        missing = [field for field in REQUIRED_FIELDS if field not in claim]
        if missing:
            errors.append(f"{prefix}: 缺少字段 {', '.join(missing)}")
            continue

        claim_id = str(claim.get("claim_id", "") or "").strip()
        claim_text = str(claim.get("claim_text", "") or "").strip()
        if not claim_id:
            errors.append(f"{prefix}: claim_id 不能为空")
        elif claim_id in seen_ids:
            errors.append(f"{prefix}: claim_id 重复：{claim_id}")
        else:
            seen_ids.add(claim_id)
        if not claim_text:
            errors.append(f"{prefix}: claim_text 不能为空")

        claim_type = str(claim.get("claim_type", "") or "").strip()
        source_type = str(claim.get("source_type", "") or "").strip()
        verification = str(claim.get("verification_status", "") or "").strip()
        public_use = str(claim.get("public_use_status", "") or "").strip()

        if claim_type not in CLAIM_TYPES:
            errors.append(f"{prefix}: 未知 claim_type：{claim_type}")
        if source_type not in SOURCE_TYPES:
            errors.append(f"{prefix}: 未知 source_type：{source_type}")
        if verification not in VERIFICATION_STATUSES:
            errors.append(f"{prefix}: 未知 verification_status：{verification}")
        if public_use not in PUBLIC_USE_STATUSES:
            errors.append(f"{prefix}: 未知 public_use_status：{public_use}")

        source_ref = str(claim.get("source_ref", "") or "").strip()
        if source_type != "model_inference" and not source_ref:
            errors.append(f"{prefix}: 非 model_inference Claim 必须填写 source_ref")

        if public_use == "ready" and verification not in {"verified", "source_only"}:
            errors.append(
                f"{prefix}: public_use_status=ready 时 verification_status 必须为 verified 或 source_only"
            )
        if source_type == "model_inference" and public_use == "ready":
            errors.append(f"{prefix}: model_inference 不能直接标记为 ready")
    return errors


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="校验医学文章 Claim Ledger JSON")
    parser.add_argument("path", help="claim-ledger.json 路径")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    path = Path(args.path).expanduser().resolve()
    if not path.is_file():
        print(f"文件不存在：{path}", file=sys.stderr)
        return 2
    try:
        claims = load_claims(path)
        errors = validate_claims(claims)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"OK: {len(claims)} claims validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
