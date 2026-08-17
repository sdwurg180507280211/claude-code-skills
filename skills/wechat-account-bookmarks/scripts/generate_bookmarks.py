#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from collections import OrderedDict
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from bookmarks import save_bookmarks
from io_utils import (
    InputEntry,
    atomic_write_json,
    identity_fingerprint,
    load_entries,
    load_json,
)
from resolver import FIELDS, now_iso, resolve_entry
from upstream import ensure_upstreams

STATE_SCHEMA_VERSION = 3


def unique_entries(entries: list[InputEntry]) -> list[InputEntry]:
    ordered: OrderedDict[str, InputEntry] = OrderedDict()
    for entry in entries:
        ordered.setdefault(entry.name, entry)
    return list(ordered.values())


def apply_default_target(entries: list[InputEntry], default_target: str) -> list[InputEntry]:
    """Apply a CLI-level target default, keeping per-row non-auto preferences."""
    if default_target == "auto":
        return entries
    return [
        InputEntry(
            entry.name,
            entry.folder,
            entry.url,
            entry.biz,
            target_pref=entry.target_pref if entry.target_pref != "auto" else default_target,
        )
        for entry in entries
    ]


def is_identity_resolved(item: dict) -> bool:
    return (
        str(item.get("identity_status", "") or "") == "resolved"
        and bool(str(item.get("target_url", "") or "").strip())
    )


def write_csv(path: Path, rows: list[dict], fields: list[str] = FIELDS) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def load_state(path: Path, fingerprint: str, no_resume: bool) -> dict[str, dict]:
    if no_resume:
        return {}
    raw = load_json(path, {})
    if not isinstance(raw, dict):
        return {}
    if raw.get("schema_version") != STATE_SCHEMA_VERSION:
        return {}
    if raw.get("identity_fingerprint") != fingerprint:
        return {}
    results = raw.get("results")
    return results if isinstance(results, dict) else {}


def save_state(path: Path, fingerprint: str, results: dict[str, dict]) -> None:
    atomic_write_json(
        path,
        {
            "schema_version": STATE_SCHEMA_VERSION,
            "identity_fingerprint": fingerprint,
            "updated_at": now_iso(),
            "results": results,
        },
    )


def build_outputs(
    output_dir: Path,
    entries: list[InputEntry],
    results: dict[str, dict],
    root_folder: str,
    strip_prefix: str | None,
) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    unique = unique_entries(entries)
    rows: list[dict] = []
    unresolved: list[dict] = []
    bookmark_review: list[dict] = []

    for entry in unique:
        item = dict(results.get(entry.name) or {field: "" for field in FIELDS})
        item["original_name"] = entry.name
        item["folder"] = entry.folder
        item["input_url"] = entry.url
        rows.append(item)
        if not is_identity_resolved(item):
            unresolved.append(item)
        else:
            bookmark_status = str(item.get("bookmark_status", "") or "")
            fallback_status = str(item.get("fallback_status", "") or "")
            if bookmark_status != "direct_ok" or fallback_status != "present":
                bookmark_review.append(item)

    write_csv(output_dir / "wechat_accounts.csv", rows)
    write_csv(output_dir / "unresolved.csv", unresolved)
    write_csv(output_dir / "bookmark_review.csv", bookmark_review)
    save_bookmarks(
        output_dir / "bookmarks.html",
        entries,
        results,
        root_folder=root_folder,
        strip_prefix=strip_prefix,
    )

    redirect_map = {
        entry.name: {
            "name": entry.name,
            "current_name": (results.get(entry.name) or {}).get("current_name", ""),
            "biz": (results.get(entry.name) or {}).get("biz", ""),
            "homepage_url": (results.get(entry.name) or {}).get("homepage_url", ""),
            "fallback_article_url": (results.get(entry.name) or {}).get("fallback_article_url", ""),
            "target_type": (results.get(entry.name) or {}).get("target_type", ""),
            "target_url": (results.get(entry.name) or {}).get("target_url", ""),
            "identity_status": (results.get(entry.name) or {}).get("identity_status", ""),
            "bookmark_status": (results.get(entry.name) or {}).get("bookmark_status", ""),
            "fallback_status": (results.get(entry.name) or {}).get("fallback_status", ""),
            "resolved_by": (results.get(entry.name) or {}).get("resolved_by", ""),
            "error_code": (results.get(entry.name) or {}).get("error_code", ""),
        }
        for entry in unique
        if is_identity_resolved(results.get(entry.name) or {})
    }
    atomic_write_json(output_dir / "redirect-map.json", redirect_map)

    identity_counts: dict[str, int] = {}
    bookmark_counts: dict[str, int] = {}
    target_counts: dict[str, int] = {}
    for entry in unique:
        item = results.get(entry.name) or {}
        identity = str(item.get("identity_status", "") or "unknown")
        bookmark = str(item.get("bookmark_status", "") or "unknown")
        target_type = str(item.get("target_type", "") or "none")
        identity_counts[identity] = identity_counts.get(identity, 0) + 1
        bookmark_counts[bookmark] = bookmark_counts.get(bookmark, 0) + 1
        target_counts[target_type] = target_counts.get(target_type, 0) + 1

    resolved = sum(1 for entry in unique if is_identity_resolved(results.get(entry.name) or {}))
    summary = {
        "input_rows": len(entries),
        "unique_names": len(unique),
        "identity_resolved": resolved,
        "identity_unresolved": len(unique) - resolved,
        "bookmark_review": len(bookmark_review),
        "fallback_missing": sum(
            1
            for entry in unique
            if is_identity_resolved(results.get(entry.name) or {})
            and str((results.get(entry.name) or {}).get("fallback_status", "") or "") != "present"
        ),
        "identity_status_counts": identity_counts,
        "bookmark_status_counts": bookmark_counts,
        "target_type_counts": target_counts,
        "bookmarks_file": str((output_dir / "bookmarks.html").resolve()),
        "generated_at": now_iso(),
    }
    atomic_write_json(output_dir / "run_summary.json", summary)
    return summary


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="批量生成微信公众号主页/文章浏览器书签")
    parser.add_argument("--input", required=True, help="输入 .xlsx 或 .csv")
    parser.add_argument("--sheet", default=None, help="Excel Sheet 名称；默认第一个")
    parser.add_argument("--name-column", default=None, help="公众号名称列；默认自动识别")
    parser.add_argument("--folder-column", default=None, help="文件夹列；默认自动识别")
    parser.add_argument("--url-column", default=None, help="历史公众号文章 URL 列；默认自动识别")
    parser.add_argument("--biz-column", default=None, help="已知 biz/__biz 列；默认自动识别")
    parser.add_argument("--target-column", default=None, help="目标类型列（auto/homepage/article）；默认自动识别")
    parser.add_argument("--output-dir", default="output", help="输出目录")
    parser.add_argument("--root-folder", default="微信公众号", help="书签根目录")
    parser.add_argument("--strip-folder-prefix", default="桌面", help="移除输入目录第一层；空字符串关闭")
    parser.add_argument("--delay", type=float, default=1.5, help="需要后台搜索的公众号之间等待秒数")
    parser.add_argument("--max-items", type=int, default=None, help="仅处理前 N 个唯一公众号，用于试跑")
    parser.add_argument("--validate-homepage", action="store_true", help="额外验证 profile_ext；未能证明正常时标为 unknown")
    parser.add_argument("--prepare-only", action="store_true", help="只规范化输入，不访问微信或安装上游")
    parser.add_argument("--retry-unresolved", action="store_true", help="重试 state 中未解析项")
    parser.add_argument("--no-resume", action="store_true", help="忽略 state.json 全部重跑")
    target_group = parser.add_mutually_exclusive_group()
    target_group.add_argument(
        "--target",
        choices=["auto", "homepage", "article"],
        default="auto",
        help="全局目标类型：auto 优先主页、article 强制文章、homepage 强制主页",
    )
    target_group.add_argument(
        "--prefer-article",
        dest="target",
        action="store_const",
        const="article",
        help="等价于 --target article：所有书签强制指向公众号文章",
    )
    parser.add_argument("--discovery-limit", type=int, default=5, help="名称搜索时最多让上游发现多少篇候选文章")
    parser.add_argument(
        "--session",
        default=str(Path.home() / ".cache/wechat-article-archive/session.json"),
        help="复用苍何 archive skill 的微信公众平台会话缓存",
    )
    parser.add_argument(
        "--upstream-cache",
        default=str(Path.home() / ".cache/wechat-account-bookmarks/upstream"),
        help="苍何上游 Skill 的固定版本缓存目录",
    )
    parser.add_argument("--archive-repo", default=None, help="已存在的 wechat-article-archive-skill 路径")
    parser.add_argument("--extractor-repo", default=None, help="已存在的 wechat-article-extractor-skill 路径")
    parser.add_argument("--no-upstream-bootstrap", action="store_true", help="禁止自动 clone/npm ci；要求显式提供本地上游路径")
    return parser.parse_args()


def write_normalized_input(output_dir: Path, entries: list[InputEntry]) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    unique = unique_entries(entries)
    rows = [
        {
            "公众号名称": entry.name,
            "文件夹结构": entry.folder,
            "URL": entry.url,
            "biz": entry.biz,
            "目标类型": entry.target_pref,
            "解析优先级": (
                "input_biz"
                if entry.biz
                else "input_article_url_verify"
                if entry.url
                else "upstream_archive"
            ),
        }
        for entry in unique
    ]
    path = output_dir / "input_normalized.csv"
    fields = ["公众号名称", "文件夹结构", "URL", "biz", "目标类型", "解析优先级"]
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "input_rows": len(entries),
        "unique_names": len(unique),
        "duplicate_rows_removed": len(entries) - len(unique),
        "with_biz": sum(1 for e in unique if e.biz),
        "with_url": sum(1 for e in unique if e.url),
        "with_article_pref": sum(1 for e in unique if e.target_pref == "article"),
        "with_homepage_pref": sum(1 for e in unique if e.target_pref == "homepage"),
        "name_search_needed": sum(1 for e in unique if not e.biz and not e.url),
        "normalized_file": str(path.resolve()),
        "generated_at": now_iso(),
    }
    atomic_write_json(output_dir / "input_summary.json", summary)
    return summary


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.is_file():
        print(f"输入文件不存在：{input_path}", file=sys.stderr)
        return 2
    if args.discovery_limit < 1 or args.delay < 0:
        print("--discovery-limit 必须 > 0，--delay 不能为负数", file=sys.stderr)
        return 2

    output_dir = Path(args.output_dir).expanduser().resolve()
    strip_prefix = args.strip_folder_prefix.strip() or None

    try:
        entries, input_meta = load_entries(
            input_path,
            sheet_name=args.sheet,
            name_column=args.name_column,
            folder_column=args.folder_column,
            url_column=args.url_column,
            biz_column=args.biz_column,
            target_column=args.target_column,
        )
    except Exception as exc:
        print(f"读取输入失败：{exc}", file=sys.stderr)
        return 2

    if not entries:
        print("输入中没有可处理的公众号名称", file=sys.stderr)
        return 2

    entries = apply_default_target(entries, args.target)

    if args.max_items is not None:
        if args.max_items <= 0:
            print("--max-items 必须大于 0", file=sys.stderr)
            return 2
        allowed = {entry.name for entry in unique_entries(entries)[: args.max_items]}
        entries = [entry for entry in entries if entry.name in allowed]

    if args.prepare_only:
        print(json.dumps(write_normalized_input(output_dir, entries), ensure_ascii=False, indent=2))
        return 0

    unique = unique_entries(entries)
    fingerprint = identity_fingerprint(unique)
    output_dir.mkdir(parents=True, exist_ok=True)
    state_path = output_dir / "state.json"
    results = load_state(state_path, fingerprint, args.no_resume)

    atomic_write_json(
        output_dir / "input_meta.json",
        {
            "input": str(input_path),
            **input_meta,
            "input_rows": len(entries),
            "unique_names": len(unique),
            "identity_fingerprint": fingerprint,
        },
    )

    pending: list[InputEntry] = []
    for entry in unique:
        existing = results.get(entry.name) or {}
        if is_identity_resolved(existing):
            continue
        if existing and not args.retry_unresolved and not args.no_resume:
            continue
        pending.append(entry)

    print(f"输入行数：{len(entries)}；唯一公众号：{len(unique)}；本次待处理：{len(pending)}")

    # Explicit biz can be used without network access. Article URLs must pass
    # through the upstream extractor so the article/account name is not silently
    # bound to the wrong Excel row. Pure names need archive discovery as before.
    needs_upstream = any(not entry.biz for entry in pending)
    upstream = None
    if needs_upstream:
        try:
            upstream = ensure_upstreams(
                Path(args.upstream_cache),
                archive_repo=Path(args.archive_repo) if args.archive_repo else None,
                extractor_repo=Path(args.extractor_repo) if args.extractor_repo else None,
                bootstrap=not args.no_upstream_bootstrap,
            )
        except Exception as exc:
            print(f"准备苍何上游 Skill 失败：{exc}", file=sys.stderr)
            build_outputs(output_dir, entries, results, args.root_folder, strip_prefix)
            return 3

    adapter_script = SCRIPT_DIR / "extract_identity.js"
    session_path = Path(args.session).expanduser()
    work_dir = output_dir / ".tmp"
    work_dir.mkdir(parents=True, exist_ok=True)

    for index, entry in enumerate(pending, start=1):
        print(f"[{index}/{len(pending)}] {entry.name}")
        result = resolve_entry(
            entry,
            upstream=upstream,
            adapter_script=adapter_script,
            session_path=session_path,
            work_dir=work_dir,
            validate=args.validate_homepage,
            discovery_limit=args.discovery_limit,
        )

        if result.get("identity_status") == "session_expired":
            print("    → 上游登录态失效；重新执行当前项以触发正常扫码登录", file=sys.stderr)
            result = resolve_entry(
                entry,
                upstream=upstream,
                adapter_script=adapter_script,
                session_path=session_path,
                work_dir=work_dir,
                validate=args.validate_homepage,
                discovery_limit=args.discovery_limit,
            )

        results[entry.name] = result
        save_state(state_path, fingerprint, results)
        print(
            f"    → identity={result.get('identity_status')} "
            f"bookmark={result.get('bookmark_status')} "
            f"target={result.get('target_type')} "
            f"by={result.get('resolved_by')} biz={result.get('biz', '')}"
        )

        if result.get("identity_status") == "rate_limited":
            print("检测到微信频控，停止后续请求并保留断点。", file=sys.stderr)
            summary = build_outputs(output_dir, entries, results, args.root_folder, strip_prefix)
            print(json.dumps(summary, ensure_ascii=False, indent=2))
            return 4

        if index < len(pending) and args.delay > 0 and not entry.biz:
            time.sleep(args.delay)

    summary = build_outputs(output_dir, entries, results, args.root_folder, strip_prefix)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["identity_unresolved"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
