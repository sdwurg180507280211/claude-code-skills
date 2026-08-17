#!/usr/bin/env python3
from __future__ import annotations

import os
import runpy
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent

# Keep the existing implementation intact, but provide portable defaults at the
# skill boundary instead of relying on one developer machine's absolute paths.
os.environ.setdefault("OCR_SCRIPT", str(SCRIPT_DIR / "ocr_wechat.swift"))
os.environ.setdefault("ADB_PATH", shutil.which("adb") or "adb")

if not os.environ.get("ANDROID_SERIAL"):
    adb = os.environ["ADB_PATH"]
    try:
        proc = subprocess.run(
            [adb, "devices"],
            check=False,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=10,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        print(f"无法执行 adb：{exc}", file=sys.stderr)
        raise SystemExit(2)

    devices = []
    for line in proc.stdout.splitlines()[1:]:
        parts = line.split()
        if len(parts) >= 2 and parts[1] == "device":
            devices.append(parts[0])

    if len(devices) == 1:
        os.environ["ANDROID_SERIAL"] = devices[0]
    elif not devices:
        print("没有发现可用 Android 设备；请连接设备并确认 adb devices。", file=sys.stderr)
        raise SystemExit(2)
    else:
        print(
            "发现多个 Android 设备；请设置 ANDROID_SERIAL 后再运行。",
            file=sys.stderr,
        )
        raise SystemExit(2)

runpy.run_path(str(SCRIPT_DIR / "_batch_add_wechat_impl.py"), run_name="__main__")
