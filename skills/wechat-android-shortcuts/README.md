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
└── scripts/
    ├── batch_add_wechat.py
    ├── _batch_add_wechat_impl.py
    └── ocr_wechat.swift
```

`batch_add_wechat.py` 是可移植入口：自动使用当前 Skill 内的 OCR 脚本，并在只连接一台 Android 设备时自动选择 serial。原有已验证的微信 UI 自动化实现保存在 `_batch_add_wechat_impl.py`。

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

## 详细经验

设备适配、OCR 坐标、ADBKeyBoard、MIUI、视频号、小程序、桌面验证等完整记录见：

```text
references/adb-desktop-shortcuts.md
```

## 与浏览器书签 Skill 的关系

- `wechat-account-bookmarks`：公众号身份 / 文章 URL / biz → Edge / Chrome 书签。
- `wechat-android-shortcuts`：公众号 / 小程序 → 微信 App → Android 桌面真实图标。

两者独立运行，不互相 import。需要时可以使用同一份公众号名称清单作为输入来源。
