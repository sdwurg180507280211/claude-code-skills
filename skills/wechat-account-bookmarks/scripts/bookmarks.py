#!/usr/bin/env python3
from __future__ import annotations

import html
import time
from pathlib import Path
from urllib.parse import urlencode

from io_utils import InputEntry, normalize_folder


def build_homepage_url(biz: str) -> str:
    query = urlencode({"action": "home", "__biz": biz, "scene": "124"})
    return f"https://mp.weixin.qq.com/mp/profile_ext?{query}#wechat_redirect"


def build_tree(entries: list[InputEntry], result_by_name: dict[str, dict], root_folder: str, strip_prefix: str | None):
    root = {"folders": {}, "bookmarks": []}
    seen: set[tuple[tuple[str, ...], str, str]] = set()

    for entry in entries:
        result = result_by_name.get(entry.name) or {}
        url = str(result.get("homepage_url", "") or "").strip()
        if not url:
            continue
        folders = [root_folder] + normalize_folder(entry.folder, strip_prefix)
        key = (tuple(folders), entry.name, url)
        if key in seen:
            continue
        seen.add(key)

        node = root
        for folder in folders:
            node = node["folders"].setdefault(folder, {"folders": {}, "bookmarks": []})
        node["bookmarks"].append((entry.name, url))
    return root


def _render_node(node: dict, indent: int = 0) -> list[str]:
    pad = "    " * indent
    lines: list[str] = []
    add_date = str(int(time.time()))

    for folder_name, child in node["folders"].items():
        safe_folder = html.escape(folder_name, quote=True)
        lines.append(f'{pad}<DT><H3 ADD_DATE="{add_date}">{safe_folder}</H3>')
        lines.append(f"{pad}<DL><p>")
        lines.extend(_render_node(child, indent + 1))
        lines.append(f"{pad}</DL><p>")

    for title, url in node["bookmarks"]:
        safe_title = html.escape(title, quote=False)
        safe_url = html.escape(url, quote=True)
        lines.append(f'{pad}<DT><A HREF="{safe_url}" ADD_DATE="{add_date}">{safe_title}</A>')
    return lines


def render_bookmarks_html(entries: list[InputEntry], result_by_name: dict[str, dict], root_folder: str = "微信公众号", strip_prefix: str | None = "桌面") -> str:
    tree = build_tree(entries, result_by_name, root_folder, strip_prefix)
    body = _render_node(tree, 1)
    lines = [
        "<!DOCTYPE NETSCAPE-Bookmark-file-1>",
        "<!-- This is an automatically generated file.",
        "     It will be read and overwritten by browsers.",
        "     DO NOT EDIT! -->",
        '<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">',
        "<TITLE>Bookmarks</TITLE>",
        "<H1>Bookmarks</H1>",
        "<DL><p>",
        *body,
        "</DL><p>",
        "",
    ]
    return "\n".join(lines)


def save_bookmarks(path: Path, *args, **kwargs) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_bookmarks_html(*args, **kwargs), encoding="utf-8")
