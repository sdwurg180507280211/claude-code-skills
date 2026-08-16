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
    for row in accounts:
        name = str(row.get("original_name", "") or "").strip()
        if not name:
            errors.append("wechat_accounts.csv 存在空 original_name")
            continue
        if name in names:
            errors.append(f"wechat_accounts.csv 重复公众号：{name}")
        names.add(name)

        identity_status = str(row.get("identity_status", "") or "")
        biz = str(row.get("biz", "") or "").strip()
        homepage = str(row.get("homepage_url", "") or "").strip()
        if identity_status == "resolved":
            resolved_names.add(name)
            if not biz or not homepage:
                errors.append(f"{name}: resolved 但缺少 biz/homepage_url")
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
        elif homepage or biz:
            errors.append(f"{name}: identity_status={identity_status or 'empty'} 但仍带 biz/homepage_url")

    unresolved_names = {
        str(row.get("original_name", "") or "").strip()
        for row in unresolved
        if str(row.get("original_name", "") or "").strip()
    }
    expected_unresolved = names - resolved_names
    if unresolved_names != expected_unresolved:
        errors.append("unresolved.csv 与 wechat_accounts.csv 的 identity_status 不一致")

    if not bookmarks_path.is_file():
        errors.append(f"缺少文件：{bookmarks_path}")
    else:
        content = bookmarks_path.read_text(encoding="utf-8")
        hrefs = [html.unescape(x) for x in re.findall(r'<A\s+HREF="([^"]+)"', content, flags=re.I)]
        bookmark_biz = []
        for href in hrefs:
            try:
                q = parse_qs(urlsplit(href).query)
                bookmark_biz.append((q.get("__biz") or [""])[0])
            except ValueError:
                bookmark_biz.append("")
        if len(hrefs) != len(resolved_names):
            errors.append(
                f"bookmarks.html 条目数 {len(hrefs)} 与 resolved 数量 {len(resolved_names)} 不一致"
            )
        if any(not biz for biz in bookmark_biz):
            errors.append("bookmarks.html 存在缺少 __biz 的书签")

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
