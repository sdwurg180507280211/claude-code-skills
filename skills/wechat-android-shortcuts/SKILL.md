---
name: wechat-android-shortcuts
description: 通过 ADB 驱动 Android 手机上的微信官方“添加到桌面”流程，为微信公众号或小程序创建、检查真实桌面快捷方式。使用截图 + macOS Vision OCR 定位微信界面，适用于“把公众号加到手机桌面”“ADB 批量创建微信快捷方式”“检查桌面微信快捷方式 Chat_User”等任务；不修改微信数据库、不伪造 ShortcutInfo、不绕过系统或微信权限。
---

# 微信 Android 桌面快捷方式

## 定位

本 Skill 只负责 Android 真机上的微信桌面快捷方式自动化：

```text
公众号 / 小程序名称
→ ADB 控制 Android 真机
→ 微信搜索
→ OCR 识别候选与按钮
→ 进入公众号 / 小程序
→ 微信官方“添加到桌面”
→ 可选验证桌面图标与 Chat_User
```

浏览器 Edge / Chrome 书签不属于本 Skill；需要 `bookmarks.html` 时使用 `wechat-account-bookmarks`。

## 核心原则

- 只走微信官方“添加到桌面”入口，不直接写 Launcher 或微信数据库。
- 不伪造 `ShortcutInfo`、`shortcut_id`、`Chat_User` 映射。
- 模糊匹配只用于找候选；进入资料页后必须二次核对身份。
- 公众号优先于视频号，小程序优先级最低但可尝试专用添加流程。
- 微信内部 `uiautomator dump` 可能为空，因此主要用截图 + OCR，而不是依赖 UI XML。
- 找不到入口、身份无法确认或机型不兼容时跳过并记录，不盲点固定坐标。

## 环境

```text
macOS
Python 3
Swift（系统自带，用于 Vision OCR）
Android Platform Tools / adb
Android 真机 + USB 调试
微信 App
ADBKeyBoard（需要稳定中文输入时）
```

运行前确认设备：

```bash
adb devices -l
```

如果只连接一台授权设备，入口脚本会自动选择；多台设备时必须显式设置：

```bash
ANDROID_SERIAL=<serial> python3 scripts/batch_add_wechat.py 公众号1 公众号2
```

也可覆盖 ADB 或 OCR 路径：

```bash
ADB_PATH=/path/to/adb \
ANDROID_SERIAL=<serial> \
OCR_SCRIPT=/path/to/ocr_wechat.swift \
python3 scripts/batch_add_wechat.py 公众号1 公众号2
```

## 批量添加

```bash
python3 scripts/batch_add_wechat.py 公众号1 公众号2 公众号3
```

入口脚本负责提供可移植的 ADB / OCR 默认值，再调用现有批量实现。

批量流程大致为：

```text
进入微信搜索
→ 输入名称
→ 进入“账号”结果
→ 按公众号 / 服务号 / 媒体 / 视频号 / 小程序优先级找候选
→ 资料页二次核验
→ 如未关注则关注
→ 公众号：••• → 设置 → 添加到桌面
→ 小程序：••• → 转发给朋友所在横向菜单 → 添加到桌面
→ 继续下一个
```

## OCR

```bash
adb exec-out screencap -p > /tmp/screen.png
swift scripts/ocr_wechat.swift /tmp/screen.png
```

OCR 输出为：

```text
x,y widthxheight<TAB>识别文本
```

按钮坐标必须以实时 OCR 为主。脚本中的少量固定坐标只是 OCR 找不到时的兼容兜底，不应视为跨设备稳定契约。

## 检查快捷方式

点击桌面图标后，可只读检查微信 Activity / Fragment 参数：

```bash
adb shell dumpsys activity -p com.tencent.mm activities
```

公众号桌面快捷方式通常可看到类似：

```text
Chat_User=gh_...
```

完整操作、设备适配和已知坑见：

```text
references/adb-desktop-shortcuts.md
```

## 已知边界

- 微信版本、Android ROM、分辨率、系统桌面都会影响坐标和菜单结构。
- MIUI 上通过 ADB 长按拖动创建桌面文件夹目前不稳定；本 Skill 不负责大规模桌面布局整理。
- 有些视频号没有“设置/添加到桌面”入口，应直接跳过。
- 小程序和公众号的“添加到桌面”入口不同，不要混用流程。
- ADBKeyBoard 使用结束后应恢复用户原输入法。

## 安全边界

- 不执行 `pm clear`。
- 不删除或篡改微信数据库。
- 不批量删除用户桌面快捷方式。
- 不绕过 USB 调试授权、系统弹窗或微信权限确认。
- 不因为 OCR 模糊匹配就直接确认身份。
