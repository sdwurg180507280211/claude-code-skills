#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
import re
from dataclasses import dataclass
from pathlib import Path


NAME_CANDIDATES = ["快捷方式名称", "公众号名称", "内容名称", "名称", "name"]
FOLDER_CANDIDATES = ["文件夹结构", "分类", "文件夹", "folder", "category"]


@dataclass(frozen=True)
class InputEntry:
    name: str
    folder: str = ""


def _norm_header(value: object) -> str:
    return str(value or "").strip()


def choose_column(headers: list[str], requested: str | None, candidates: list[str], required: bool) -> str | None:
    if requested:
        if requested not in headers:
            raise ValueError(f"找不到列：{requested}；现有列：{headers}")
        return requested
    for candidate in candidates:
        if candidate in headers:
            return candidate
    if required:
        raise ValueError(f"无法自动识别名称列；现有列：{headers}")
    return None


def load_csv(path: Path, name_column: str | None, folder_column: str | None) -> tuple[list[InputEntry], str, str | None]:
    with path.open("r", encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        headers = [_norm_header(h) for h in (reader.fieldnames or [])]
        name_col = choose_column(headers, name_column, NAME_CANDIDATES, True)
        folder_col = choose_column(headers, folder_column, FOLDER_CANDIDATES, False)
        entries: list[InputEntry] = []
        for row in reader:
            name = str(row.get(name_col, "") or "").strip()
            if not name:
                continue
            folder = str(row.get(folder_col, "") or "").strip() if folder_col else ""
            entries.append(InputEntry(name=name, folder=folder))
    return entries, name_col, folder_col


def load_xlsx(path: Path, sheet_name: str | None, name_column: str | None, folder_column: str | None) -> tuple[list[InputEntry], str, str | None, str]:
    try:
        from openpyxl import load_workbook
    except ImportError as exc:
        raise RuntimeError("读取 .xlsx 需要 openpyxl，请先 pip install -r requirements.txt") from exc

    wb = load_workbook(path, read_only=True, data_only=True)
    if sheet_name:
        if sheet_name not in wb.sheetnames:
            raise ValueError(f"找不到 Sheet：{sheet_name}；现有：{wb.sheetnames}")
        ws = wb[sheet_name]
    else:
        ws = wb[wb.sheetnames[0]]

    rows = ws.iter_rows(values_only=True)
    try:
        header_row = next(rows)
    except StopIteration:
        return [], name_column or "", folder_column, ws.title

    headers = [_norm_header(x) for x in header_row]
    name_col = choose_column(headers, name_column, NAME_CANDIDATES, True)
    folder_col = choose_column(headers, folder_column, FOLDER_CANDIDATES, False)
    name_idx = headers.index(name_col)
    folder_idx = headers.index(folder_col) if folder_col else None

    entries: list[InputEntry] = []
    for row in rows:
        if name_idx >= len(row):
            continue
        name = str(row[name_idx] or "").strip()
        if not name:
            continue
        folder = ""
        if folder_idx is not None and folder_idx < len(row):
            folder = str(row[folder_idx] or "").strip()
        entries.append(InputEntry(name=name, folder=folder))
    return entries, name_col, folder_col, ws.title


def load_entries(path: Path, sheet_name: str | None = None, name_column: str | None = None, folder_column: str | None = None) -> tuple[list[InputEntry], dict]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        entries, name_col, folder_col = load_csv(path, name_column, folder_column)
        return entries, {"sheet": None, "name_column": name_col, "folder_column": folder_col}
    if suffix == ".xlsx":
        entries, name_col, folder_col, sheet = load_xlsx(path, sheet_name, name_column, folder_column)
        return entries, {"sheet": sheet, "name_column": name_col, "folder_column": folder_col}
    raise ValueError("只支持 .xlsx 和 .csv 输入")


def normalize_folder(folder: str, strip_prefix: str | None) -> list[str]:
    if not folder:
        return []
    parts = [part.strip() for part in re.split(r"\s*>\s*", folder) if part.strip()]
    if len(parts) <= 1 and "/" in folder:
        parts = [part.strip() for part in folder.split("/") if part.strip()]
    if strip_prefix and parts and parts[0] == strip_prefix:
        parts = parts[1:]
    return parts


def atomic_write_json(path: Path, data: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def load_json(path: Path, default):
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return default
