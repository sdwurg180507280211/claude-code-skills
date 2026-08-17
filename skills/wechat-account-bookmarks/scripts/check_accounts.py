#!/usr/bin/env python3
"""Check whether WeChat official accounts exist by exact-name search.

This is a lighter alternative to generate_bookmarks.py when the user only needs
to know which public accounts exist / do not exist. It uses the same upstream
wechat-article-archive-skill session, but only calls the searchbiz endpoint and
does not fetch article history, which avoids the article-list frequency control.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import csv
import importlib.util
import json
import sys
import threading
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from io_utils import atomic_write_json, load_entries  # noqa: E402

DEFAULT_ARCHIVE_REPO = (
    Path.home() / ".cache/wechat-account-bookmarks/upstream/wechat-article-archive-skill"
)
DEFAULT_SESSION = Path.home() / ".cache/wechat-article-archive/session.json"


def load_upstream_module(archive_repo: Path):
    script = Path(archive_repo).expanduser() / "scripts" / "discover_account_articles.py"
    if not script.is_file():
        raise FileNotFoundError(f"找不到上游脚本：{script}")
    spec = importlib.util.spec_from_file_location("discover_account_articles", script)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def unique_entries(entries):
    seen = set()
    result = []
    for entry in entries:
        if entry.name in seen:
            continue
        seen.add(entry.name)
        result.append(entry)
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="按精确名称检查微信公众号是否存在")
    parser.add_argument("--input", required=True, help="输入 .xlsx 或 .csv")
    parser.add_argument("--sheet", default=None, help="Excel Sheet 名称；默认第一个")
    parser.add_argument("--name-column", default=None, help="公众号名称列；默认自动识别")
    parser.add_argument("--output-dir", default="output-existence", help="输出目录")
    parser.add_argument("--delay", type=float, default=1.5, help="每个名称之间的等待秒数")
    parser.add_argument("--workers", type=int, default=1, help="并发线程数；加速时建议 2-4，并配合较小 --delay")
    parser.add_argument("--max-items", type=int, default=None, help="最多检查前 N 个唯一名称")
    parser.add_argument("--retries", type=int, default=3, help="单个名称失败后的重试次数")
    parser.add_argument("--timeout", type=int, default=15, help="上游请求超时秒数")
    parser.add_argument("--login-timeout", type=int, default=180, help="需要扫码时的等待秒数")
    parser.add_argument(
        "--session",
        default=str(DEFAULT_SESSION),
        help="微信公众平台 session.json 路径",
    )
    parser.add_argument(
        "--archive-repo",
        default=str(DEFAULT_ARCHIVE_REPO),
        help="wechat-article-archive-skill 仓库路径",
    )
    parser.add_argument("--qr-path", default="/tmp/wechat-check-login-qr.jpg", help="扫码二维码图片保存路径")
    parser.add_argument("--no-login", action="store_true", help="没有 session 时不尝试扫码，直接报错退出")
    parser.add_argument("--retry-errors", action="store_true", help="重试 state 中 status=error 的名称")
    return parser.parse_args()


def check_name(mod, client, name: str, retries: int, base_wait: float) -> dict:
    last_error = ""
    for attempt in range(retries + 1):
        try:
            accounts = client.search_accounts(name)
            exact = [
                a for a in accounts
                if str(a.get("nickname", "") or "").strip() == name
            ]
            if exact:
                return {
                    "status": "exists",
                    "fakeid": str(exact[0].get("fakeid", "") or "").strip(),
                    "nickname": str(exact[0].get("nickname", "") or "").strip(),
                    "similar": "",
                    "error": "",
                }
            if accounts:
                similar = [str(a.get("nickname", "") or "").strip() for a in accounts[:5]]
                return {
                    "status": "review",
                    "fakeid": "",
                    "nickname": "",
                    "similar": " | ".join(similar),
                    "error": "没有精确匹配，但存在相似名称",
                }
            return {
                "status": "missing",
                "fakeid": "",
                "nickname": "",
                "similar": "",
                "error": "搜索无结果",
            }
        except mod.AuthError:
            raise
        except Exception as exc:  # noqa: BLE001 - upstream raises RuntimeError for freq control etc.
            last_error = f"{type(exc).__name__}: {exc}"
            if attempt < retries:
                wait = base_wait * (2 ** attempt)
                print(f"    [{name}] 查询失败，{wait:.1f}s 后重试 ({attempt + 1}/{retries}): {last_error}",
                      file=sys.stderr)
                time.sleep(wait)
    return {
        "status": "error",
        "fakeid": "",
        "nickname": "",
        "similar": "",
        "error": last_error,
    }


def write_results(output_dir: Path, entries, state: dict, summary: dict) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for entry in entries:
        item = state.get(entry.name, {})
        rows.append(
            {
                "快捷方式名称": entry.name,
                "文件夹结构": entry.folder,
                "URL": entry.url,
                "biz": entry.biz,
                "status": item.get("status", "pending"),
                "fakeid": item.get("fakeid", ""),
                "similar": item.get("similar", ""),
                "error": item.get("error", ""),
            }
        )

    fieldnames = ["快捷方式名称", "文件夹结构", "URL", "biz", "status", "fakeid", "similar", "error"]
    with (output_dir / "all_results.csv").open("w", encoding="utf-8-sig", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    for status, filename in [
        ("exists", "existing.csv"),
        ("missing", "missing.csv"),
        ("review", "review.csv"),
        ("error", "error.csv"),
    ]:
        filtered = [r for r in rows if r["status"] == status]
        with (output_dir / filename).open("w", encoding="utf-8-sig", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(filtered)

    atomic_write_json(output_dir / "run_summary.json", summary)


def main() -> int:
    args = parse_args()
    input_path = Path(args.input).expanduser().resolve()
    if not input_path.is_file():
        print(f"输入文件不存在：{input_path}", file=sys.stderr)
        return 2

    output_dir = Path(args.output_dir).expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    try:
        entries, _meta = load_entries(
            input_path,
            sheet_name=args.sheet,
            name_column=args.name_column,
        )
    except Exception as exc:
        print(f"读取输入失败：{exc}", file=sys.stderr)
        return 2

    if not entries:
        print("输入中没有可检查的公众号名称", file=sys.stderr)
        return 2

    unique = unique_entries(entries)
    if args.max_items is not None:
        if args.max_items <= 0:
            print("--max-items 必须大于 0", file=sys.stderr)
            return 2
        unique = unique[: args.max_items]

    mod = load_upstream_module(Path(args.archive_repo).expanduser())

    session_path = Path(args.session).expanduser()
    session_data = mod.load_session(session_path)
    if session_data is None:
        if args.no_login:
            print("没有可用 session，且 --no-login 已设置；请先登录微信公众平台", file=sys.stderr)
            return 2
        print("没有可用 session，准备扫码登录……", file=sys.stderr)
        import requests  # noqa: PLC0415 - needed to persist the cookie session

        token, cookie = mod.qr_login(Path(args.qr_path).expanduser(), args.login_timeout)
        cookie_session = requests.Session()
        for part in cookie.split("; "):
            if "=" in part:
                name, value = part.split("=", 1)
                cookie_session.cookies.set(name, value)
        mod.save_session(session_path, token, cookie_session)
        token, cookie = token, cookie
    else:
        token, cookie = session_data

    client = mod.DashboardClient(
        token, cookie, timeout=args.timeout, retries=min(args.retries, 2)
    )

    state_path = output_dir / "state.json"
    state = {}
    if state_path.is_file():
        try:
            loaded = json.loads(state_path.read_text(encoding="utf-8"))
            if isinstance(loaded, dict):
                state = loaded
        except (OSError, ValueError):
            state = {}

    pending = [
        entry
        for entry in unique
        if entry.name not in state
        or (args.retry_errors and state.get(entry.name, {}).get("status") == "error")
    ]
    start = time.time()
    checked = 0
    stopped = False

    if args.workers <= 1:
        try:
            for index, entry in enumerate(pending, start=1):
                print(f"[{index}/{len(pending)}] {entry.name}", flush=True)
                result = check_name(mod, client, entry.name, args.retries, args.delay)
                state[entry.name] = result
                atomic_write_json(state_path, state)
                checked += 1
                print(
                    f"    → {result.get('status')}"
                    + (f" fakeid={result.get('fakeid')}" if result.get("fakeid") else "")
                    + (f" error={result.get('error')}" if result.get("error") else ""),
                    flush=True,
                )
                if index < len(pending) and args.delay > 0:
                    time.sleep(args.delay)
        except mod.AuthError:
            session_path.unlink(missing_ok=True)
            print("微信 session 已过期，已停止并删除 session；需要重新扫码后继续", file=sys.stderr)
            stopped = True
    else:
        thread_local = threading.local()

        def get_client():
            if not hasattr(thread_local, "client"):
                thread_local.client = mod.DashboardClient(
                    token, cookie, timeout=args.timeout, retries=min(args.retries, 2)
                )
            return thread_local.client

        def process(entry):
            c = get_client()
            return entry.name, check_name(mod, c, entry.name, args.retries, args.delay)

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as executor:
                future_to_entry = {
                    executor.submit(process, entry): entry for entry in pending
                }
                for future in concurrent.futures.as_completed(future_to_entry):
                    entry = future_to_entry[future]
                    name, result = future.result()
                    state[name] = result
                    atomic_write_json(state_path, state)
                    checked += 1
                    print(
                        f"[{checked}/{len(pending)}] {name} → {result.get('status')}"
                        + (f" fakeid={result.get('fakeid')}" if result.get("fakeid") else "")
                        + (f" error={result.get('error')}" if result.get("error") else ""),
                        flush=True,
                    )
        except mod.AuthError:
            stopped = True
            session_path.unlink(missing_ok=True)
            print("微信 session 已过期，已停止并删除 session；需要重新扫码后继续", file=sys.stderr)

    elapsed = time.time() - start
    counts = {"exists": 0, "missing": 0, "review": 0, "error": 0, "pending": 0}
    for entry in unique:
        item = state.get(entry.name, {})
        status = item.get("status", "pending")
        counts[status] = counts.get(status, 0) + 1

    summary = {
        "input_rows": len(entries),
        "unique_names": len(unique),
        "checked_now": checked,
        "stopped_early": stopped,
        "elapsed_seconds": round(elapsed, 2),
        "status_counts": counts,
        "output_dir": str(output_dir.resolve()),
        "state_file": str(state_path.resolve()),
    }
    write_results(output_dir, entries, state, summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0 if not stopped and counts.get("pending", 0) == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
