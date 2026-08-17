#!/usr/bin/env python3
from __future__ import annotations

import base64
import os
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
ADB = os.environ.get("ADB_PATH") or shutil.which("adb") or "adb"
SERIAL = os.environ.get("ANDROID_SERIAL", "").strip()
OCR_SCRIPT = os.environ.get("OCR_SCRIPT") or str(SCRIPT_DIR / "ocr_wechat.swift")
ADB_KEYBOARD_IME = os.environ.get("ADB_KEYBOARD_IME", "com.android.adbkeyboard/.AdbIME")
TMP = os.environ.get("WECHAT_SHORTCUT_TMP", "/tmp/batch_wechat")

os.makedirs(TMP, exist_ok=True)


def parse_adb_devices(output: str) -> list[str]:
    devices: list[str] = []
    for line in (output or "").splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            devices.append(parts[0])
    return devices


def ensure_serial() -> str:
    global SERIAL
    if SERIAL:
        return SERIAL
    try:
        proc = subprocess.run(
            [ADB, "devices"],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise RuntimeError(f"无法执行 adb：{exc}") from exc
    devices = parse_adb_devices(proc.stdout)
    if len(devices) == 1:
        SERIAL = devices[0]
        return SERIAL
    if not devices:
        raise RuntimeError("没有发现可用 Android 设备；请连接设备并确认 adb devices。")
    raise RuntimeError("发现多个 Android 设备；请设置 ANDROID_SERIAL 后再运行。")


def sh(args: list[str]) -> subprocess.CompletedProcess:
    serial = ensure_serial()
    return subprocess.run([ADB, "-s", serial] + args, capture_output=True, text=True)


def shell(cmd: str) -> subprocess.CompletedProcess:
    return sh(["shell", cmd])


def tap(x: int, y: int) -> None:
    sh(["shell", "input", "tap", str(x), str(y)])


def swipe(x1: int, y1: int, x2: int, y2: int, d: int = 200) -> None:
    sh(["shell", "input", "swipe", str(x1), str(y1), str(x2), str(y2), str(d)])


def screencap(path: str) -> str:
    serial = ensure_serial()
    with open(path, "wb") as f:
        subprocess.run([ADB, "-s", serial, "exec-out", "screencap", "-p"], stdout=f, check=False)
    return path


def ocr(path: str) -> list[dict]:
    r = subprocess.run(["swift", OCR_SCRIPT, path], capture_output=True, text=True)
    items = []
    for line in r.stdout.splitlines():
        m = re.match(r"([\d.]+),([\d.]+) ([\d.]+)x([\d.]+)\t(.*)", line)
        if m:
            x = float(m.group(1))
            y = float(m.group(2))
            w = float(m.group(3))
            h = float(m.group(4))
            text = m.group(5).strip()
            items.append({"x": x, "y": y, "w": w, "h": h, "text": text})
    return items


def find(items: list[dict], *subs: str, ymin: float = 0, ymax: float = 99999, xmin: float = 0, xmax: float = 99999):
    for it in items:
        if ymin <= it["y"] <= ymax and xmin <= it["x"] <= xmax:
            for s in subs:
                if s in it["text"]:
                    return it
    return None


def center(it: dict) -> tuple[float, float]:
    return (it["x"] + it["w"] / 2, it["y"] + it["h"] / 2)


def tap_item(it: dict) -> None:
    x, y = center(it)
    tap(int(x), int(y))


def broadcast(action: str, extra_key: str | None = None, extra_val: str | None = None) -> None:
    serial = ensure_serial()
    cmd = [ADB, "-s", serial, "shell", "am", "broadcast", "-a", action]
    if extra_key:
        cmd += ["--es", extra_key, extra_val or ""]
    subprocess.run(cmd, capture_output=True, text=True)


def matches_search(text: str, name: str) -> bool:
    """搜索/候选匹配：短名称完整命中，长名称以前 6 个字找候选。仅用于找候选。"""
    compact_text = text.replace("-", "").replace(" ", "")
    compact_name = name.replace("-", "").replace(" ", "")
    if len(compact_name) <= 6:
        return name in text or compact_name in compact_text
    prefix6 = compact_name[:6]
    return prefix6 in compact_text or name[:6] in text


def matches_full(text: str, name: str) -> bool:
    """资料页最终校验：必须完整匹配目标名称，允许忽略连接符和空格。"""
    if name in text:
        return True
    compact_name = name.replace("-", "").replace(" ", "")
    compact_text = text.replace("-", "").replace(" ", "")
    return bool(compact_name and compact_name in compact_text)


def matches_confirm(text: str, name: str) -> bool:
    """小程序确认：完整名优先；截断候选要求更长前缀；未截断候选检查特征后缀。"""
    if matches_full(text, name):
        return True
    compact_text = text.replace("-", "").replace(" ", "").replace("…", "")
    compact_name = name.replace("-", "").replace(" ", "")
    truncated = "…" in text or len(compact_text) < len(compact_name)
    if truncated:
        min_prefix = min(8, len(compact_name))
        return compact_name[:min_prefix] in compact_text
    if len(compact_name) > 6:
        suffix = compact_name[-3:] if len(compact_name) >= 9 else compact_name[-2:]
        return suffix in compact_text
    return False


def pick_candidates(items: list[dict], name: str) -> list[tuple[dict, str]]:
    """按 OCR 行聚类候选，并按公众号/服务号/媒体/视频号/小程序优先级排序。"""
    priority = ["公众号", "服务号", "媒体", "视频号", "小程序"]
    matched = [it for it in items if 500 <= it["y"] <= 2600 and matches_search(it["text"], name)]
    matched.sort(key=lambda it: it["y"])
    groups: list[list[dict]] = []
    for it in matched:
        if groups and it["y"] - groups[-1][-1]["y"] < 150:
            groups[-1].append(it)
        else:
            groups.append([it])
    cands = []
    seen = set()
    for g in groups:
        main = g[0]
        ymin = main["y"] - 120
        ymax = g[-1]["y"] + 250
        label = None
        pri = len(priority)
        for i, lbl in enumerate(priority):
            if find(items, lbl, ymin=ymin, ymax=ymax, xmin=0, xmax=1200):
                label = lbl
                pri = i
                break
        if not label:
            continue
        key = (main["text"].strip(), label)
        if key not in seen:
            seen.add(key)
            cands.append((pri, main, label))
    cands.sort(key=lambda x: x[0])
    return [(it, label) for _, it, label in cands]


def top_activity_from_dumpsys(text: str) -> str:
    for pattern in (
        r"topResumedActivity=ActivityRecord\{[^}]*?\s([^\s}]+/[^\s}]+)",
        r"mResumedActivity: ActivityRecord\{[^}]*?\s([^\s}]+/[^\s}]+)",
    ):
        m = re.search(pattern, text or "")
        if m:
            return m.group(1)
    return ""


def tap_search_icon() -> None:
    shot = screencap(f"{TMP}/nav.png")
    items = ocr(shot)
    qitem = None
    for it in items:
        if it["y"] <= 350 and "q" in it["text"].lower() and it["x"] >= 500:
            qitem = it
            break
    if qitem:
        if qitem["w"] <= 160:
            x = qitem["x"] + qitem["w"] / 2
        else:
            x = qitem["x"] + qitem["w"] - 180
        y = qitem["y"] + qitem["h"] / 2
        print(f"  tap magnifier at ({x:.0f},{y:.0f})", flush=True)
        tap(int(x), int(y))
    else:
        print("  Q not found by OCR, fallback tap (972,210)", flush=True)
        tap(972, 210)
    time.sleep(0.8)


def is_mini_program() -> bool:
    r = sh(["shell", "dumpsys", "activity", "activities"]).stdout
    top = top_activity_from_dumpsys(r).lower()
    if "appbrand" in top:
        return True
    for line in r.splitlines():
        low = line.lower()
        if "appbrand" in low and ("resumedactivity" in low or "topresumedactivity" in low or "mcurrentfocus" in low):
            return True
    return False


def handle_mini_program_add() -> bool:
    print("  handle_mini_program_add", flush=True)
    tap(1100, 210)
    time.sleep(2)
    shot = screencap(f"{TMP}/mini_menu.png")
    items = ocr(shot)
    row = find(items, "转发到朋友", ymin=1500, ymax=2500)
    if not row:
        print("  !! 转发到朋友 not found", flush=True)
        return False
    y = row["y"] + row["h"] / 2
    swipe(1000, int(y), 300, int(y), 300)
    time.sleep(1)
    shot = screencap(f"{TMP}/mini_add.png")
    items = ocr(shot)
    add = find(items, "添加到桌面", ymin=1000, ymax=2500)
    if not add:
        print("  !! 添加到桌面 not found in mini menu", flush=True)
        return False
    tap_item(add)
    time.sleep(1.5)
    shell("input keyevent 4")
    time.sleep(1)
    return True


def process(name: str, first: bool = False) -> bool:
    print(f"=== Processing: {name} ===", flush=True)
    b64 = base64.b64encode(name.encode("utf-8")).decode()

    act = sh(["shell", "dumpsys", "activity", "activities"]).stdout
    top_act = top_activity_from_dumpsys(act)
    if "FTSMainUI" in top_act or "MMFTSSOSHomeWebViewUI" in top_act:
        shell("input tap 500 220; sleep 0.3")
    elif "NewBizInfoSettingUI" in top_act:
        shell("input keyevent 4; sleep 0.4")
        tap_search_icon()
        shell("input tap 500 220; sleep 0.3")
    elif first:
        tap_search_icon()
        shell("input tap 500 220; sleep 0.3")
    else:
        shell("input keyevent 4; sleep 0.4")
        tap_search_icon()
        shell("input tap 500 220; sleep 0.3")
    time.sleep(1.0)
    broadcast("ADB_CLEAR_TEXT")
    time.sleep(0.5)
    broadcast("ADB_INPUT_B64", "msg", b64)
    time.sleep(2.0)

    shot = screencap(f"{TMP}/suggest.png")
    items = ocr(shot)
    sug = None
    for it in items:
        if 300 <= it["y"] <= 700 and it["text"].lstrip().startswith("Q") and matches_search(it["text"], name):
            sug = it
            break
    if not sug:
        for it in items:
            if 300 <= it["y"] <= 700 and matches_search(it["text"], name):
                sug = it
                break
    if sug:
        print(f"  tap suggestion at {center(sug)}", flush=True)
        tap_item(sug)
        time.sleep(2.5)
    else:
        print("  !! no suggestion found, skip", flush=True)
        return False

    shot = screencap(f"{TMP}/result.png")
    items = ocr(shot)
    acct = find(items, "账号", ymin=300, ymax=500)
    attempts = 0
    while not acct and attempts < 8:
        print(f"  no 账号 tab, small left swipe #{attempts + 1}", flush=True)
        swipe(700, 370, 500, 370, 200)
        time.sleep(1)
        shot = screencap(f"{TMP}/result_swipe{attempts}.png")
        items = ocr(shot)
        acct = find(items, "账号", ymin=300, ymax=500)
        attempts += 1
    if acct:
        print(f"  tap 账号 at {center(acct)}", flush=True)
        tap_item(acct)
        time.sleep(2.5)
    else:
        print("  !! 账号 tab not found after swipes, skip", flush=True)
        return False

    tried = set()
    verified = False
    for attempt in range(3):
        shot = screencap(f"{TMP}/account_try{attempt}.png")
        items = ocr(shot)
        cand = None
        cand_label = None
        for it, label in pick_candidates(items, name):
            key = (it["text"].strip(), label)
            if key not in tried:
                cand = it
                cand_label = label
                break
        if not cand:
            swipe(600, 1800, 600, 900, 400)
            time.sleep(1.5)
            shot = screencap(f"{TMP}/account_try{attempt}_scroll.png")
            items = ocr(shot)
            for it, label in pick_candidates(items, name):
                key = (it["text"].strip(), label)
                if key not in tried:
                    cand = it
                    cand_label = label
                    break
        if not cand:
            print("  !! no more candidates, skip", flush=True)
            return False
        key = (cand["text"].strip(), cand_label)
        tried.add(key)
        print(f"  candidate {attempt + 1}/3: tap {center(cand)}", flush=True)
        tap_item(cand)
        time.sleep(3.0)

        shot = screencap(f"{TMP}/profile_verify.png")
        items = ocr(shot)
        add_now = find(items, "添加到桌面", ymin=300, ymax=1800)
        if add_now:
            print("  already on settings, tap 添加到桌面", flush=True)
            tap_item(add_now)
            time.sleep(1.5)
            return True
        gzh_link = find(items, "公众号：", ymin=0, ymax=1500)
        is_video_profile = find(items, "视频号", ymin=0, ymax=1500) or find(items, "主页", ymin=0, ymax=1500)
        if gzh_link and is_video_profile:
            print(f"  video profile, tap linked 公众号 at {center(gzh_link)}", flush=True)
            tap_item(gzh_link)
            time.sleep(2.5)
            shot = screencap(f"{TMP}/after_gzh_link.png")
            items = ocr(shot)
            add_now = find(items, "添加到桌面", ymin=300, ymax=1800)
            if add_now:
                print(f"  tap 添加到桌面 at {center(add_now)}", flush=True)
                tap_item(add_now)
                time.sleep(1.5)
                return True
        if is_mini_program():
            list_ok = matches_confirm(cand["text"], name)
            page_ok = any(matches_full(it["text"], name) for it in items if it["y"] < 1500)
            if not list_ok and not page_ok:
                print("  mini program name mismatch, back and try next candidate", flush=True)
                shell("input keyevent 4")
                time.sleep(1.5)
                continue
            print("  mini program verified by search name, use mini program add flow", flush=True)
            if handle_mini_program_add():
                return True
            shell("input keyevent 4")
            time.sleep(1.5)
            continue
        name_ok = any(matches_full(it["text"], name) for it in items if it["y"] < 1500)
        if name_ok:
            verified = True
            break
        print("  profile name mismatch, back and try another candidate", flush=True)
        shell("input keyevent 4")
        time.sleep(1.5)
    if not verified:
        print("  !! profile not verified after candidates, skip", flush=True)
        return False

    shot = screencap(f"{TMP}/profile.png")
    items = ocr(shot)
    followed = find(items, "已关注", ymin=800, ymax=2000, xmin=0, xmax=1200)
    follow = None
    if not followed:
        follow = find(items, "关注服务号", "关注公众号", ymin=800, ymax=2000, xmin=0, xmax=700)
        if not follow:
            follow = find(items, "关注", ymin=800, ymax=2000, xmin=100, xmax=600)
    if followed:
        print("  already followed, skip follow", flush=True)
    elif follow:
        print(f"  tap follow at {center(follow)}", flush=True)
        tap_item(follow)
        time.sleep(2.0)

    shot = screencap(f"{TMP}/after_follow.png")
    items = ocr(shot)
    if not find(items, "私信") and not find(items, "关注"):
        print("  in chat, tap avatar", flush=True)
        tap(1100, 210)
        time.sleep(2.5)

    setting = None
    for mx, my in [(1100, 210), (1140, 210), (1080, 250), (1100, 260), (1050, 220)]:
        tap(mx, my)
        time.sleep(1.5)
        shot = screencap(f"{TMP}/menu_try.png")
        items = ocr(shot)
        setting = find(items, "设置", ymin=1500, ymax=2200)
        if setting:
            print(f"  menu opened with tap ({mx},{my})", flush=True)
            break
    if not setting:
        print("  menu not opened, trying to close banner X", flush=True)
        for cx, cy in [(1150, 150), (1100, 160), (1050, 150)]:
            tap(cx, cy)
            time.sleep(0.8)
        for mx, my in [(1100, 210), (1140, 210)]:
            tap(mx, my)
            time.sleep(1.5)
            shot = screencap(f"{TMP}/menu_try2.png")
            items = ocr(shot)
            setting = find(items, "设置", ymin=1500, ymax=2200)
            if setting:
                break
    if setting:
        print(f"  tap 设置 at {center(setting)}", flush=True)
        tap_item(setting)
        time.sleep(2.0)
    else:
        print("  !! menu not opened (banner may cover), skip", flush=True)
        return False

    shot = screencap(f"{TMP}/settings.png")
    items = ocr(shot)
    add = find(items, "添加到桌面", ymin=300, ymax=1800)
    if add:
        print(f"  tap 添加到桌面 at {center(add)}", flush=True)
        tap_item(add)
        time.sleep(1.5)
        return True
    print("  !! 添加到桌面 not found", flush=True)
    return False


def get_default_ime() -> str:
    proc = sh(["shell", "settings", "get", "secure", "default_input_method"])
    value = (proc.stdout or "").strip()
    return "" if value in {"", "null"} else value


def set_ime(ime: str) -> bool:
    if not ime:
        return False
    proc = sh(["shell", "ime", "set", ime])
    combined = f"{proc.stdout}\n{proc.stderr}".lower()
    return proc.returncode == 0 and "error" not in combined


def run_batch(names: list[str]) -> int:
    ensure_serial()
    original_ime = get_default_ime()
    try:
        if not set_ime(ADB_KEYBOARD_IME):
            print(
                f"无法启用 ADBKeyBoard：{ADB_KEYBOARD_IME}；请先安装/启用或设置 ADB_KEYBOARD_IME。",
                file=sys.stderr,
            )
            return 2
        for i, name in enumerate(names):
            try:
                ok = process(name, first=(i == 0))
                print(f"RESULT {name}: {'OK' if ok else 'SKIP/FAIL'}", flush=True)
            except Exception as exc:
                print(f"RESULT {name}: ERROR {exc}", flush=True)
        return 0
    finally:
        if original_ime:
            if set_ime(original_ime):
                print(f"Batch done, IME restored: {original_ime}", flush=True)
            else:
                print(f"Batch done, but failed to restore IME: {original_ime}", file=sys.stderr, flush=True)
        else:
            print("Batch done; original IME could not be determined, no restore attempted.", file=sys.stderr, flush=True)


def main(argv: list[str] | None = None) -> int:
    names = list(sys.argv[1:] if argv is None else argv)
    if not names:
        print("用法：python3 scripts/batch_add_wechat.py 公众号1 公众号2 ...", file=sys.stderr)
        return 2
    if not Path(OCR_SCRIPT).is_file():
        print(f"OCR 脚本不存在：{OCR_SCRIPT}", file=sys.stderr)
        return 2
    try:
        return run_batch(names)
    except RuntimeError as exc:
        print(str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
