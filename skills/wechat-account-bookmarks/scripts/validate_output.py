#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
from pathlib import Path
from urllib.parse import parse_qs, urlsplit


def read_csv(path: Path) -> list[dict]:
    if not path.is_file():
        raise ValueError(f"缺少文件：{path}")
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def validate(output_dir: Path) -> list[str]:
    errors: list[str] = []
    accounts_path = output_dir / "wechat_accounts.csv"
    unresolved_path = output_dir / "unresolved.csv"
    bookmarks_path = output_dir / "bookmarks.html"
    summary_path = output_dir / "run_summary.json"

    try:
        accounts = read_csv(accounts_path)
        unresolved = read_csv(unresolved_path)
    except ValueError as exc:
        return [str(exc)]

    names: set[str] = set()
    resolved_names: set[str] = set()
    resolved_targets: dict[str, str] = {}
    for row in accounts:
        name = str(row.get("original_name", "") or "").strip()
        if not name:
            errors.append("wechat_accounts.csv 存在空 original_name")
            continue
        if name in names:
            errors.append(f"wechat_accounts.csv 重复公众号：{name}")
        names.add(name)

        identity_status = str(row.get("identity_status", "") or "")
        target_type = str(row.get("target_type", "") or "").strip()
        target_url = str(row.get("target_url", "") or "").strip()
        biz = str(row.get("biz", "") or "").strip()
        homepage = str(row.get("homepage_url", "") or "").strip()
        fallback = str(row.get("fallback_article_url", "") or "").strip()

        if identity_status == "resolved":
            resolved_names.add(name)
            if target_type not in {"homepage", "article"} or not target_url:
                errors.append(f"{name}: resolved 但缺少有效 target_type/target_url")
                continue
            resolved_targets[name] = target_url

            if target_type == "homepage":
                if not biz or not homepage or target_url != homepage:
                    errors.append(f"{name}: homepage target 缺少 biz/homepage_url 或 target_url 不一致")
                    continue
                try:
                    parts = urlsplit(homepage)
                    query = parse_qs(parts.query)
                    url_biz = (query.get("__biz") or [""])[0]
                except ValueError:
                    errors.append(f"{name}: homepage_url 无法解析")
                    continue
                if parts.scheme != "https" or parts.netloc != "mp.weixin.qq.com":
                    errors.append(f"{name}: homepage_url 不是 mp.weixin.qq.com HTTPS")
                if url_biz != biz:
                    errors.append(f"{name}: homepage_url 的 __biz 与 biz 不一致")
            elif target_type == "article":
                if not fallback or target_url != fallback:
                    errors.append(f"{name}: article target 必须与 fallback_article_url 一致")
        elif target_url:
            errors.append(f"{name}: identity_status={identity_status or 'empty'} 却存在 target_url")

    unresolved_names = {
        str(row.get("original_name", "") or "").strip()
        for row in unresolved
        if str(row.get("original_name", "") or "").strip()
    }
    expected_unresolved = names - resolved_names
    if unresolved_names != expected_unresolved:
        errors.append("unresolved.csv 与 wechat_accounts.csv 的 identity_status/target_url 不一致")

    if not bookmarks_path.is_file():
        errors.append(f"缺少文件：{bookmarks_path}")
    else:
        content = bookmarks_path.read_text(encoding="utf-8")
        hrefs = [html.unescape(x) for x in re.findall(r'<A\s+HREF="([^"]+)"', content, flags=re.I)]
        expected_hrefs = set(resolved_targets.values())
        actual_hrefs = set(hrefs)
        missing = expected_hrefs - actual_hrefs
        if missing:
            errors.append(f"bookmarks.html 缺少 {len(missing)} 个已解析 target_url")
        unexpected = actual_hrefs - expected_hrefs
        if unexpected:
            errors.append(f"bookmarks.html 存在 {len(unexpected)} 个不属于 resolved 记录的 URL")

    if not summary_path.is_file():
        errors.append(f"缺少文件：{summary_path}")
    else:
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            if int(summary.get("unique_names", -1)) != len(names):
                errors.append("run_summary.json unique_names 与 CSV 不一致")
            if int(summary.get("identity_resolved", -1)) != len(resolved_names):
                errors.append("run_summary.json identity_resolved 与 CSV 不一致")
        except (OSError, ValueError, TypeError):
            errors.append("run_summary.json 无法解析")

    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description="校验 wechat-account-bookmarks 输出契约")
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()
    errors = validate(args.output_dir.expanduser().resolve())
    if errors:
        print("输出校验失败：", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1
    print("OK: output contract validated")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
