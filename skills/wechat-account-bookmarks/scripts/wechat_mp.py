#!/usr/bin/env python3
from __future__ import annotations

import html
import json
import os
import re
import sys
import time
import uuid
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

import requests

BASE = "https://mp.weixin.qq.com"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124 Safari/537.36"
    ),
    "Referer": f"{BASE}/",
    "Origin": BASE,
    "Accept-Encoding": "identity",
}


class AuthError(RuntimeError):
    pass


@dataclass
class SessionData:
    token: str
    cookie: str


def load_session(path: Path) -> SessionData | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        token = str(data.get("token", "")).strip()
        cookie = str(data.get("cookie", "")).strip()
        if token and cookie:
            return SessionData(token=token, cookie=cookie)
    except (OSError, ValueError, TypeError):
        return None
    return None


def save_session(path: Path, token: str, session: requests.Session) -> SessionData:
    path.parent.mkdir(parents=True, exist_ok=True)
    cookie = "; ".join(f"{item.name}={item.value}" for item in session.cookies)
    payload = {"token": token, "cookie": cookie}
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    try:
        os.chmod(path, 0o600)
    except OSError:
        pass
    return SessionData(token=token, cookie=cookie)


def delete_session(path: Path) -> None:
    try:
        path.unlink(missing_ok=True)
    except OSError:
        pass


def qr_login(session_path: Path, timeout: int = 180) -> SessionData:
    """Login to WeChat MP using the normal QR flow and cache the resulting session."""
    session = requests.Session()
    session.headers.update(HEADERS)
    session.get(f"{BASE}/", timeout=20)

    response = session.post(
        f"{BASE}/cgi-bin/bizlogin",
        params={"action": "startlogin"},
        data={
            "userlang": "zh_CN",
            "redirect_url": "",
            "login_type": 3,
            "sessionid": uuid.uuid4().hex,
            "token": "",
            "lang": "zh_CN",
            "f": "json",
            "ajax": 1,
        },
        timeout=20,
    )
    response.raise_for_status()
    data = response.json()
    if (data.get("base_resp") or {}).get("ret") not in (0, None):
        raise AuthError(f"startlogin failed: {data}")
    if not session.cookies.get("uuid"):
        raise AuthError("startlogin did not return a uuid cookie")

    qr_response = session.get(
        f"{BASE}/cgi-bin/scanloginqrcode",
        params={"action": "getqrcode", "random": int(time.time() * 1000)},
        timeout=20,
    )
    qr_response.raise_for_status()
    if not qr_response.content.startswith((b"\xff\xd8\xff", b"\x89PNG", b"GIF8")):
        raise AuthError("QR endpoint did not return an image")

    qr_path = session_path.with_name("login-qr.png")
    qr_path.parent.mkdir(parents=True, exist_ok=True)
    qr_path.write_bytes(qr_response.content)
    print(f"请扫码并在微信中确认登录：{qr_path}", file=sys.stderr)
    try:
        webbrowser.open(qr_path.resolve().as_uri())
    except Exception:
        pass

    deadline = time.time() + timeout
    while time.time() < deadline:
        result = session.get(
            f"{BASE}/cgi-bin/scanloginqrcode",
            params={"action": "ask", "lang": "zh_CN", "f": "json", "ajax": 1},
            timeout=20,
        ).json()
        if result.get("status") == 1:
            break
        time.sleep(2)
    else:
        raise AuthError(f"QR login timed out after {timeout} seconds")

    result = session.post(
        f"{BASE}/cgi-bin/bizlogin",
        params={"action": "login"},
        data={
            "userlang": "zh_CN",
            "redirect_url": "",
            "cookie_forbidden": 0,
            "cookie_cleaned": 0,
            "plugin_used": 0,
            "login_type": 3,
            "token": "",
            "lang": "zh_CN",
            "f": "json",
            "ajax": 1,
        },
        timeout=20,
    ).json()

    match = re.search(r"[?&]token=(\d+)", result.get("redirect_url", ""))
    if not match:
        raise AuthError(f"login did not return a token: {result}")

    data = save_session(session_path, match.group(1), session)
    try:
        qr_path.unlink(missing_ok=True)
    except OSError:
        pass
    return data


class DashboardClient:
    def __init__(self, session_data: SessionData, timeout: int = 20, retries: int = 2):
        self.token = session_data.token
        self.timeout = timeout
        self.retries = retries
        self.session = requests.Session()
        self.session.headers.update({**HEADERS, "Cookie": session_data.cookie})

    def get_json(self, path: str, params: dict[str, object]) -> dict:
        params = dict(params)
        params.update({"token": self.token, "lang": "zh_CN", "f": "json", "ajax": 1})
        last_error: Exception | None = None
        for attempt in range(self.retries + 1):
            try:
                response = self.session.get(
                    f"{BASE}{path}", params=params, timeout=self.timeout
                )
                response.raise_for_status()
                data = response.json()
                ret = (data.get("base_resp") or {}).get("ret")
                if ret == 200003:
                    raise AuthError("dashboard session expired")
                if ret not in (0, None):
                    raise RuntimeError(f"WeChat API returned ret={ret}: {data}")
                return data
            except AuthError:
                raise
            except (requests.RequestException, ValueError, RuntimeError) as exc:
                last_error = exc
                if attempt < self.retries:
                    time.sleep(min(2**attempt, 8))
        raise RuntimeError(f"WeChat API failed: {last_error}")

    def search_accounts(self, query: str, count: int = 10) -> list[dict]:
        data = self.get_json(
            "/cgi-bin/searchbiz",
            {
                "action": "search_biz",
                "begin": 0,
                "count": count,
                "query": query,
            },
        )
        return data.get("list", []) or []

    def exact_account(self, query: str) -> dict | None:
        query_clean = query.strip()
        accounts = self.search_accounts(query_clean)
        matches = [
            item
            for item in accounts
            if str(item.get("nickname", "")).strip() == query_clean
        ]
        if len(matches) == 1:
            return matches[0]
        if len(matches) > 1:
            raise ValueError(f"exact nickname returned {len(matches)} records")
        return None

    def list_articles(self, fakeid: str, begin: int = 0, count: int = 5) -> list[dict]:
        data = self.get_json(
            "/cgi-bin/appmsgpublish",
            {
                "sub": "list",
                "sub_action": "list_ex",
                "type": "101_1",
                "free_publish_type": 1,
                "fakeid": fakeid,
                "begin": begin,
                "count": count,
                "query": "",
            },
        )
        page_raw = data.get("publish_page") or "{}"
        page = json.loads(page_raw) if isinstance(page_raw, str) else page_raw
        articles: list[dict] = []
        for publication in page.get("publish_list", []) or []:
            info_raw = publication.get("publish_info") or "{}"
            info = json.loads(info_raw) if isinstance(info_raw, str) else info_raw
            articles.extend(info.get("appmsgex", []) or [])
        return articles


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


def parse_biz_from_html(text: str) -> str:
    if not text:
        return ""
    candidates = [
        r"\bvar\s+biz\s*=\s*['\"]([^'\"]+)['\"]",
        r"['\"]__biz['\"]\s*:\s*['\"]([^'\"]+)['\"]",
        r"[?&](?:__biz|biz)=([^&#'\"\s]+)",
    ]
    for pattern in candidates:
        match = re.search(pattern, text)
        if match:
            return unquote(html.unescape(match.group(1))).strip()
    return ""


def get_article_link(article: dict) -> str:
    for key in ("link", "url", "content_url"):
        value = str(article.get(key, "") or "").strip()
        if value:
            return html.unescape(value)
    return ""


def get_article_title(article: dict) -> str:
    for key in ("title", "msg_title"):
        value = str(article.get(key, "") or "").strip()
        if value:
            return value
    return ""


def fetch_biz_from_article_page(url: str, timeout: int = 20) -> str:
    if not url:
        return ""
    try:
        response = requests.get(url, headers=HEADERS, timeout=timeout)
        response.raise_for_status()
        return parse_biz_from_html(response.text)
    except requests.RequestException:
        return ""
