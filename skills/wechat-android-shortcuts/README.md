# WeChat Android Shortcuts Skill

通过 ADB 操作 Android 真机上的微信官方“添加到桌面”流程，为微信公众号或小程序创建、检查真实桌面快捷方式。

这个 Skill 从 `wechat-account-bookmarks` 中拆出，专门处理设备自动化；浏览器 Edge / Chrome 的 `bookmarks.html` 继续由 `wechat-account-bookmarks` 负责。

## 能力边界

```text
公众号 / 小程序名称
→ ADB 控制微信
→ 截图 + macOS Vision OCR
→ 搜索并核验候选
→ 微信官方“添加到桌面”
→ 可选检查 Chat_User=gh_...
```

不修改微信数据库，不伪造 ShortcutInfo，不直接写 Launcher 数据。

## 文件

```text
wechat-android-shortcuts/
├── SKILL.md
├── README.md
├── references/
│   └── adb-desktop-shortcuts.md
├── scripts/
│   ├── batch_add_wechat.py
│   └── ocr_wechat.swift
└── tests/
    └── test_core.py
```

`batch_add_wechat.py` 是唯一批量入口，不再依赖拆分时遗留的 `_impl` 包装层，也不包含开发机绝对路径或固定设备 serial。默认使用当前 Skill 内的 OCR 脚本；仅连接一台 Android 设备时自动选择 serial，多设备时要求显式设置 `ANDROID_SERIAL`。

运行前会读取当前默认输入法，临时切换到 ADBKeyBoard，并通过 `try/finally` 在批量任务结束或异常后恢复原输入法，不再硬编码某台手机的搜狗输入法。

## 环境要求

```text
macOS
Python 3
Swift / Vision
adb
Android 真机 + USB 调试
微信
ADBKeyBoard（中文输入推荐）
```

先确认设备：

```bash
adb devices -l
```

## 批量添加

```bash
python3 scripts/batch_add_wechat.py 央视网 央视新闻 "大众新闻-大众日报"
```

多设备时：

```bash
ANDROID_SERIAL=<serial> \
python3 scripts/batch_add_wechat.py 公众号1 公众号2
```

自定义工具路径：

```bash
ADB_PATH=/path/to/adb \
ANDROID_SERIAL=<serial> \
OCR_SCRIPT=/path/to/ocr_wechat.swift \
ADB_KEYBOARD_IME=com.android.adbkeyboard/.AdbIME \
python3 scripts/batch_add_wechat.py 公众号1 公众号2
```

## OCR 调试

```bash
adb exec-out screencap -p > /tmp/screen.png
swift scripts/ocr_wechat.swift /tmp/screen.png
```

## 运行逻辑

公众号：

```text
微信搜索
→ “账号”筛选
→ 公众号/服务号/媒体优先候选
→ 资料页完整名称二次核验
→ 关注（如需要）
→ •••
→ 设置
→ 添加到桌面
```

小程序：

```text
微信搜索
→ 小程序候选
→ 搜索名/页面二次确认
→ 右上角 •••
→ 找“转发给朋友”横向菜单
→ 向左滑
→ 添加到桌面
```

## 离线测试

无需连接手机即可验证设备列表解析、名称匹配、候选排序、Activity 解析和输入法恢复逻辑：

```bash
python3 -m unittest discover -s tests -v
```

GitHub Actions 会同时执行 Python 编译检查和这组离线测试；真实微信 UI / ROM / 分辨率兼容性仍需真机验证。

## 详细经验

设备适配、OCR 坐标、ADBKeyBoard、MIUI、视频号、小程序、桌面验证等完整记录见：

```text
references/adb-desktop-shortcuts.md
```

## 与浏览器书签 Skill 的关系

- `wechat-account-bookmarks`：公众号身份 / 文章 URL / biz → Edge / Chrome 书签。
- `wechat-android-shortcuts`：公众号 / 小程序 → 微信 App → Android 桌面真实图标。

两者独立运行，不互相 import。需要时可以使用同一份公众号名称清单作为输入来源。
