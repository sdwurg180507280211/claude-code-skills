#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import sys
import time
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path

import requests

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from bookmarks import build_homepage_url, save_bookmarks
from io_utils import InputEntry, atomic_write_json, load_entries, load_json
from wechat_mp import (
    AuthError,
    DashboardClient,
    delete_session,
    fetch_biz_from_article_page,
    get_article_link,
    get_article_title,
    load_session,
    parse_biz_from_url,
    qr_login,
)

FIELDS = [
    "original_name",
    "current_name",
    "alias",
    "fakeid",
    "biz",
    "homepage_url",
    "fallback_article_url",
    "fallback_article_title",
    "folder",
    "status",
    "validation_http_status",
    "validation_final_url",
    "error",
    "last_verified_at",
]


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def validate_homepage(url: str, timeout: int = 15) -> dict:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
        ),
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
    }
    try:
        response = requests.get(url, headers=headers, timeout=timeout, allow_redirects=True)
    except requests.RequestException as exc:
        return {
            "status": "homepage_http_error",
            "validation_http_status": "",
            "validation_final_url": "",
            "error": f"homepage request failed: {exc}",
        }

    text = (response.text or "")[:300000]
    lower = text.lower()
    if response.status_code >= 400:
        status = "homepage_http_error"
    elif any(marker in text for marker in ["请在微信客户端打开", "请使用微信打开", "微信客户端打开"]):
        status = "homepage_requires_wechat"
    elif any(marker in text for marker in ["环境异常", "访问过于频繁", "请输入验证码", "安全验证", "操作频繁"]):
        status = "homepage_verification"
    elif any(marker in text for marker in ["帐号已自主注销", "账号已自主注销", "帐号已注销", "账号已注销", "帐号被屏蔽", "账号被屏蔽"]):
        status = "inactive"
    elif any(marker in text for marker in ["帐号迁移", "账号迁移", "主体迁移"]):
        status = "migrated"
    elif "no session" in lower:
        status = "homepage_requires_wechat"
    else:
        status = "homepage_ok"

    return {
        "status": status,
        "validation_http_status": str(response.status_code),
        "validation_final_url": response.url,
        "error": "",
    }


def unique_names(entries: list[InputEntry]) -> list[str]:
    ordered = OrderedDict()
    for entry in entries:
        if entry.name not in ordered:
            ordered[entry.name] = None
    return list(ordered.keys())


def first_folder_by_name(entries: list[InputEntry]) -> dict[str, str]:
    result: dict[str, str] = {}
    for entry in entries:
        result.setdefault(entry.name, entry.folder)
    return result


def resolve_account(client: DashboardClient, name: str, folder: str, skip_validation: bool) -> dict:
    result = {field: "" for field in FIELDS}
    result["original_name"] = name
    result["folder"] = folder
    result["last_verified_at"] = now_iso()

    account = client.exact_account(name)
    if not account:
        result["status"] = "not_found"
        result["error"] = "未找到 nickname 完全一致的公众号"
        return result

    current_name = str(account.get("nickname", "") or "").strip()
    fakeid = str(account.get("fakeid", "") or "").strip()
    alias = str(account.get("alias", "") or account.get("username", "") or "").strip()
    result.update({"current_name": current_name, "fakeid": fakeid, "alias": alias})
    if not fakeid:
        result["status"] = "error"
        result["error"] = "精确匹配结果缺少 fakeid"
        return result

    articles = client.list_articles(fakeid=fakeid, count=5)
    if not articles:
        result["status"] = "no_article"
        result["error"] = "未取得可用文章列表"
        return result

    chosen_link = ""
    chosen_title = ""
    biz = ""
    for article in articles:
        link = get_article_link(article)
        if not link:
            continue
        candidate_biz = parse_biz_from_url(link)
        if not candidate_biz:
            candidate_biz = fetch_biz_from_article_page(link)
        if candidate_biz:
            chosen_link = link
            chosen_title = get_article_title(article)
            biz = candidate_biz
            break
        if not chosen_link:
            chosen_link = link
            chosen_title = get_article_title(article)

    result["fallback_article_url"] = chosen_link
    result["fallback_article_title"] = chosen_title
    if not biz:
        result["status"] = "biz_not_found"
        result["error"] = "文章存在，但未能从 URL/页面解析 __biz"
        return result

    homepage_url = build_homepage_url(biz)
    result["biz"] = biz
    result["homepage_url"] = homepage_url

    if skip_validation:
        result["status"] = "resolved_unverified"
        return result

    validation = validate_homepage(homepage_url)
    result.update(validation)
    result["last_verified_at"] = now_iso()
    return result


def write_csv(path: Path, rows: list[dict], fields: list[str] = FIELDS) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def is_resolved(item: dict) -> bool:
    return bool(str(item.get("biz", "") or "").strip() and str(item.get("homepage_url", "") or "").strip())


def build_outputs(output_dir: Path, entries: list[InputEntry], state: dict[str, dict], root_folder: str, strip_prefix: str | None) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    folder_map = first_folder_by_name(entries)
    ordered_names = unique_names(entries)
    rows: list[dict] = []
    unresolved: list[dict] = []

    for name in ordered_names:
        item = dict(state.get(name) or {field: "" for field in FIELDS})
        item.setdefault("original_name", name)
        if not item.get("folder"):
            item["folder"] = folder_map.get(name, "")
        rows.append(item)
        if not is_resolved(item):
            unresolved.append(item)

    write_csv(output_dir / "wechat_accounts.csv", rows)
    write_csv(output_dir / "unresolved.csv", unresolved)
    save_bookmarks(
        output_dir / "bookmarks.html",
        entries,
        state,
        root_folder=root_folder,
        strip_prefix=strip_prefix,
    )

    redirect_map = {
        name: {
            "name": name,
            "biz": (state.get(name) or {}).get("biz", ""),
            "homepage_url": (state.get(name) or {}).get("homepage_url", ""),
            "fallback_article_url": (state.get(name) or {}).get("fallback_article_url", ""),
            "status": (state.get(name) or {}).get("status", ""),
        }
        for name in ordered_names
        if is_resolved(state.get(name) or {})
    }
    atomic_write_json(output_dir / "redirect-map.json", redirect_map)

    summary = {
        "input_rows": len(entries),
        "unique_names": len(ordered_names),
        "resolved_names": sum(1 for n in ordered_names if is_resolved(state.get(n) or {})),
        "unresolved_names": len(unresolved),
        "bookmarks_file": str((output_dir / "bookmarks.html").resolve()),
        "generated_at": now_iso(),
        "status_counts": {},
    }
    for name in ordered_names:
        status = str((state.get(name) or {}).get("status", "") or "unknown")
        summary["status_counts"][status] = summary["status_counts"].get(status, 0) + 1
    atomic_write_json(output_dir / "run_summary.json", summary)
    return summary


def make_client(session_path: Path, login_timeout: int) -> DashboardClient:
    session_data = load_session(session_path)
    if not session_data:
        session_data = qr_login(session_path, timeout=login_timeout)
    return DashboardClient(session_data)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="批量生成微信公众号主页浏览器书签")
    parser.add_argument("--input", required=True, help="输入 .xlsx 或 .csv")
    parser.add_argument("--sheet", default=None, help="Excel Sheet 名称；默认第一个")
    parser.add_argument("--name-column", default=None, help="公众号名称列；默认自动识别")
    parser.add_argument("--folder-column", default=None, help="文件夹列；默认自动识别")
    parser.add_argument("--output-dir", default="output", help="输出目录")
    parser.add_argument("--root-folder", default="微信公众号", help="书签根目录")
    parser.add_argument("--strip-folder-prefix", default="桌面", help="移除输入目录的第一层名称；传空字符串关闭")
    parser.add_argument("--delay", type=float, default=1.5, help="公众号之间等待秒数")
    parser.add_argument("--max-items", type=int, default=None, help="仅处理前 N 个唯一公众号，用于试跑")
    parser.add_argument("--validate-homepage", action="store_true", help="额外访问 profile_ext 做轻量验证；默认不验证，避免批量请求过多")
    parser.add_argument("--prepare-only", action="store_true", help="只读取/规范化输入并生成 input_normalized.csv，不登录微信")
    parser.add_argument("--retry-unresolved", action="store_true", help="断点续跑时重试未解析项")
    parser.add_argument("--no-resume", action="store_true", help="忽略 state.json，全部重新解析")
    parser.add_argument("--session", default=str(Path.home() / ".cache/wechat-account-bookmarks/session.json"), help="微信公众平台会话缓存路径")
    parser.add_argument("--login-timeout", type=int, default=180, help="扫码登录等待秒数")
    return parser.parse_args()


def write_normalized_input(output_dir: Path, entries: list[InputEntry]) -> dict:
    """Write a deterministic, de-duplicated preview of the input without touching WeChat."""
    output_dir.mkdir(parents=True, exist_ok=True)
    folder_map = first_folder_by_name(entries)
    names = unique_names(entries)
    rows = [
        {"公众号名称": name, "文件夹结构": folder_map.get(name, "")}
        for name in names
    ]
    path = output_dir / "input_normalized.csv"
    with path.open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=["公众号名称", "文件夹结构"])
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "input_rows": len(entries),
        "unique_names": len(names),
        "duplicate_rows_removed": len(entries) - len(names),
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

    output_dir = Path(args.output_dir).expanduser().resolve()
    session_path = Path(args.session).expanduser()
    strip_prefix = args.strip_folder_prefix.strip() or None

    try:
        entries, input_meta = load_entries(
            input_path,
            sheet_name=args.sheet,
            name_column=args.name_column,
            folder_column=args.folder_column,
        )
    except Exception as exc:
        print(f"读取输入失败：{exc}", file=sys.stderr)
        return 2

    if not entries:
        print("输入中没有可处理的公众号名称", file=sys.stderr)
        return 2

    if args.prepare_only:
        summary = write_normalized_input(output_dir, entries)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    names = unique_names(entries)
    if args.max_items is not None:
        if args.max_items <= 0:
            print("--max-items 必须大于 0", file=sys.stderr)
            return 2
        allowed = set(names[: args.max_items])
        entries = [entry for entry in entries if entry.name in allowed]
        names = names[: args.max_items]

    output_dir.mkdir(parents=True, exist_ok=True)
    state_path = output_dir / "state.json"
    if args.no_resume:
        try:
            state_path.unlink(missing_ok=True)
        except OSError:
            pass
        state: dict[str, dict] = {}
    else:
        state = load_json(state_path, {})
    folder_map = first_folder_by_name(entries)

    atomic_write_json(
        output_dir / "input_meta.json",
        {
            "input": str(input_path),
            **input_meta,
            "input_rows": len(entries),
            "unique_names": len(names),
        },
    )

    pending = []
    for name in names:
        existing = state.get(name) or {}
        if is_resolved(existing):
            continue
        if existing and not args.retry_unresolved and not args.no_resume:
            continue
        pending.append(name)

    print(f"输入行数：{len(entries)}；唯一公众号：{len(names)}；本次待处理：{len(pending)}")

    if pending:
        try:
            client = make_client(session_path, args.login_timeout)
        except Exception as exc:
            print(f"微信公众平台登录失败：{exc}", file=sys.stderr)
            build_outputs(output_dir, entries, state, args.root_folder, strip_prefix)
            return 3

        relogged = False
        for index, name in enumerate(pending, start=1):
            print(f"[{index}/{len(pending)}] {name}")
            try:
                result = resolve_account(
                    client,
                    name=name,
                    folder=folder_map.get(name, ""),
                    skip_validation=not args.validate_homepage,
                )
            except AuthError as exc:
                if relogged:
                    print(f"登录态再次失效，已保留断点：{exc}", file=sys.stderr)
                    build_outputs(output_dir, entries, state, args.root_folder, strip_prefix)
                    return 3
                print("登录态已失效，需要重新扫码一次。", file=sys.stderr)
                delete_session(session_path)
                try:
                    client = make_client(session_path, args.login_timeout)
                    relogged = True
                    result = resolve_account(
                        client,
                        name=name,
                        folder=folder_map.get(name, ""),
                        skip_validation=not args.validate_homepage,
                    )
                except Exception as retry_exc:
                    print(f"重新登录/重试失败，已保留断点：{retry_exc}", file=sys.stderr)
                    build_outputs(output_dir, entries, state, args.root_folder, strip_prefix)
                    return 3
            except Exception as exc:
                result = {field: "" for field in FIELDS}
                result.update(
                    {
                        "original_name": name,
                        "folder": folder_map.get(name, ""),
                        "status": "error",
                        "error": str(exc),
                        "last_verified_at": now_iso(),
                    }
                )

            state[name] = result
            atomic_write_json(state_path, state)
            print(f"    → {result.get('status')}  biz={result.get('biz', '')}")
            if index < len(pending) and args.delay > 0:
                time.sleep(args.delay)

    summary = build_outputs(output_dir, entries, state, args.root_folder, strip_prefix)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if summary["resolved_names"] > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
