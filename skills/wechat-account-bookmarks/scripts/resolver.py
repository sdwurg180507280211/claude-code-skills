#!/usr/bin/env python3
from __future__ import annotations

import csv
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

import requests

from bookmarks import build_homepage_url
from io_utils import InputEntry
from upstream import UpstreamPaths


FIELDS = [
    "original_name",
    "current_name",
    "alias",
    "account_id",
    "fakeid",
    "biz",
    "input_url",
    "homepage_url",
    "fallback_article_url",
    "fallback_article_title",
    "folder",
    "identity_status",
    "bookmark_status",
    "resolved_by",
    "validation_http_status",
    "validation_final_url",
    "error",
    "last_verified_at",
]

RATE_LIMIT_MARKERS = ["访问过于频繁", "操作频繁", "环境异常", "rate limit", "频控"]
SESSION_MARKERS = ["session expired", "dashboard session expired", "200003"]
EXTRACTOR_STATUS_BY_CODE = {
    1004: "rate_limited",
    1006: "migrated",
    2012: "inactive",
    2013: "inactive",
    2015: "migrated",
}


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")


def blank_result(entry: InputEntry) -> dict:
    result = {field: "" for field in FIELDS}
    result.update(
        {
            "original_name": entry.name,
            "input_url": entry.url,
            "folder": entry.folder,
            "identity_status": "unresolved",
            "bookmark_status": "not_available",
            "last_verified_at": now_iso(),
        }
    )
    return result


def parse_biz_from_url(url: str) -> str:
    if not url:
        return ""
    cleaned = html.unescape(str(url).strip())
    try:
        query = parse_qs(urlsplit(cleaned).query)
        biz = (query.get("__biz") or query.get("biz") or [""])[0]
        if biz:
            return unquote(str(biz)).strip()
    except ValueError:
        pass
    match = re.search(r"(?:[?&]|&amp;)(?:__biz|biz)=([^&#\s]+)", cleaned)
    return unquote(html.unescape(match.group(1))).strip() if match else ""


def _run(cmd: list[str], timeout: int = 240) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
        check=False,
    )


def _last_json_line(text: str) -> dict:
    for line in reversed((text or "").splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(value, dict):
            return value
    return {}


def _classify_error(text: str) -> str:
    lower = (text or "").lower()
    if any(marker.lower() in lower for marker in RATE_LIMIT_MARKERS):
        return "rate_limited"
    if any(marker.lower() in lower for marker in SESSION_MARKERS):
        return "session_expired"
    if "no published articles found" in lower:
        return "no_article"
    if "ambiguous or not found" in lower or "not found" in lower:
        return "not_found"
    return "error"


def extract_with_upstream(
    upstream: UpstreamPaths,
    adapter_script: Path,
    article_url: str,
    timeout: int = 60,
) -> dict:
    node = shutil.which("node")
    if not node:
        return {"ok": False, "status": "error", "message": "缺少 node 命令"}
    try:
        proc = _run(
            [node, str(adapter_script), str(upstream.extractor_script), article_url],
            timeout=timeout,
        )
    except subprocess.TimeoutExpired:
        return {"ok": False, "status": "error", "message": "upstream extractor timed out"}
    except OSError as exc:
        return {"ok": False, "status": "error", "message": f"启动 upstream extractor 失败：{exc}"}

    payload = _last_json_line(proc.stdout)
    if proc.returncode == 0 and payload.get("ok") is True:
        return payload

    code = payload.get("code")
    try:
        code_int = int(code) if code is not None else None
    except (TypeError, ValueError):
        code_int = None
    combined = "\n".join([proc.stdout, proc.stderr, str(payload.get("message", ""))])
    return {
        "ok": False,
        "status": EXTRACTOR_STATUS_BY_CODE.get(code_int, _classify_error(combined)),
        "code": code_int,
        "message": payload.get("message") or proc.stderr.strip() or "upstream extractor failed",
    }


def discover_with_upstream(
    upstream: UpstreamPaths,
    account_name: str,
    session_path: Path,
    work_dir: Path,
    limit: int = 5,
    timeout: int = 240,
) -> dict:
    digest = hashlib.sha256(account_name.encode("utf-8")).hexdigest()[:16]
    output = work_dir / f"{digest}.csv"
    qr_path = session_path.with_name("wechat-login-qr.jpg")
    cmd = [
        sys.executable,
        str(upstream.discover_script),
        "--account",
        account_name,
        "--limit",
        str(max(1, limit)),
        "--output",
        str(output),
        "--session",
        str(session_path),
        "--qr-path",
        str(qr_path),
        "--page-delay",
        "0.5",
    ]
    try:
        proc = _run(cmd, timeout=timeout)
    except subprocess.TimeoutExpired:
        return {"ok": False, "status": "error", "message": "upstream archive discovery timed out"}
    except OSError as exc:
        return {"ok": False, "status": "error", "message": f"启动 upstream archive 失败：{exc}"}

    summary = _last_json_line(proc.stdout)
    if proc.returncode != 0:
        combined = "\n".join([proc.stdout, proc.stderr])
        return {
            "ok": False,
            "status": _classify_error(combined),
            "message": proc.stderr.strip() or proc.stdout.strip() or "upstream discovery failed",
        }
    rows: list[dict] = []
    if output.is_file():
        with output.open("r", encoding="utf-8-sig", newline="") as fh:
            rows = list(csv.DictReader(fh))
    return {"ok": True, "summary": summary, "rows": rows}


def validate_homepage(
    url: str,
    expected_name: str = "",
    timeout: int = 15,
) -> dict:
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
            "bookmark_status": "http_error",
            "validation_http_status": "",
            "validation_final_url": "",
            "error": f"homepage request failed: {exc}",
        }

    text = (response.text or "")[:300000]
    lower = text.lower()
    if response.status_code >= 400:
        status = "http_error"
    elif any(marker in text for marker in ["请在微信客户端打开", "请使用微信打开", "微信客户端打开"]):
        status = "requires_wechat"
    elif any(marker in text for marker in ["环境异常", "访问过于频繁", "请输入验证码", "安全验证", "操作频繁"]):
        status = "verification"
    elif any(marker in text for marker in ["帐号已自主注销", "账号已自主注销", "帐号已注销", "账号已注销", "帐号被屏蔽", "账号被屏蔽"]):
        status = "inactive"
    elif any(marker in text for marker in ["帐号迁移", "账号迁移", "主体迁移", "该公众号已迁移"]):
        status = "migrated"
    elif "no session" in lower:
        status = "requires_wechat"
    else:
        positive_markers = ["profile_nickname", "profile_meta", "js_profile_qrcode"]
        has_profile_marker = any(marker in text for marker in positive_markers)
        name_matches = not expected_name or expected_name in text
        status = "direct_ok" if has_profile_marker and name_matches else "unknown"

    return {
        "bookmark_status": status,
        "validation_http_status": str(response.status_code),
        "validation_final_url": response.url,
        "error": "",
    }


def _finish_identity(result: dict, biz: str, resolved_by: str) -> dict:
    result["biz"] = biz
    result["homepage_url"] = build_homepage_url(biz)
    result["identity_status"] = "resolved"
    result["bookmark_status"] = "unverified"
    result["resolved_by"] = resolved_by
    result["last_verified_at"] = now_iso()
    return result


def resolve_entry(
    entry: InputEntry,
    upstream: UpstreamPaths | None,
    adapter_script: Path,
    session_path: Path,
    work_dir: Path,
    validate: bool = False,
    discovery_limit: int = 5,
) -> dict:
    result = blank_result(entry)

    if entry.biz:
        result["current_name"] = entry.name
        _finish_identity(result, entry.biz, "input_biz")
    elif entry.url:
        biz = parse_biz_from_url(entry.url)
        if biz:
            result["current_name"] = entry.name
            result["fallback_article_url"] = entry.url
            _finish_identity(result, biz, "input_article_url")
        else:
            if upstream is None:
                result["error"] = "输入 URL 不含 biz，且未启用上游 extractor"
                return result
            extracted = extract_with_upstream(upstream, adapter_script, entry.url)
            if not extracted.get("ok"):
                result["identity_status"] = extracted.get("status", "error")
                result["error"] = extracted.get("message", "")
                return result
            biz = str(extracted.get("account_biz", "") or "").strip()
            if not biz:
                result["identity_status"] = "biz_not_found"
                result["error"] = "上游 extractor 未返回 account_biz"
                return result
            result.update(
                {
                    "current_name": str(extracted.get("account_name", "") or entry.name),
                    "alias": str(extracted.get("account_alias", "") or ""),
                    "account_id": str(extracted.get("account_id", "") or ""),
                    "fallback_article_url": str(extracted.get("msg_link", "") or entry.url),
                    "fallback_article_title": str(extracted.get("msg_title", "") or ""),
                }
            )
            _finish_identity(result, biz, "upstream_extractor")
    else:
        if upstream is None:
            result["error"] = "名称检索需要上游 wechat-article-archive-skill"
            return result
        discovered = discover_with_upstream(
            upstream,
            entry.name,
            session_path=session_path,
            work_dir=work_dir,
            limit=discovery_limit,
        )
        if not discovered.get("ok"):
            result["identity_status"] = discovered.get("status", "error")
            result["error"] = discovered.get("message", "")
            return result

        summary = discovered.get("summary") or {}
        result["current_name"] = str(summary.get("account", "") or entry.name)
        result["fakeid"] = str(summary.get("fakeid", "") or "")
        rows = discovered.get("rows") or []
        for row in rows:
            article_url = str(row.get("url", "") or "").strip()
            if not article_url:
                continue
            biz = str(row.get("biz", "") or "").strip() or parse_biz_from_url(article_url)
            if biz:
                result["fallback_article_url"] = article_url
                result["fallback_article_title"] = str(row.get("title", "") or "")
                _finish_identity(result, biz, "upstream_archive")
                break
            extracted = extract_with_upstream(upstream, adapter_script, article_url)
            if extracted.get("ok") and extracted.get("account_biz"):
                result.update(
                    {
                        "current_name": str(extracted.get("account_name", "") or result["current_name"]),
                        "alias": str(extracted.get("account_alias", "") or ""),
                        "account_id": str(extracted.get("account_id", "") or ""),
                        "fallback_article_url": str(extracted.get("msg_link", "") or article_url),
                        "fallback_article_title": str(extracted.get("msg_title", "") or row.get("title", "") or ""),
                    }
                )
                _finish_identity(result, str(extracted["account_biz"]), "upstream_archive+extractor")
                break
            if extracted.get("status") == "rate_limited":
                result["identity_status"] = "rate_limited"
                result["error"] = extracted.get("message", "")
                return result
        if result["identity_status"] != "resolved":
            result["identity_status"] = "biz_not_found"
            result["error"] = "上游历史列表存在，但候选文章未能解析出 biz"
            return result

    if validate and result.get("homepage_url"):
        validation = validate_homepage(
            str(result["homepage_url"]),
            expected_name=str(result.get("current_name", "") or entry.name),
        )
        result.update(validation)
        result["last_verified_at"] = now_iso()
    return result
