# ADB 创建/检查微信公众号桌面快捷方式

> 适用于 Android 手机通过 ADB 操作微信官方“添加到桌面”能力。
> 已在一台 Xiaomi 2311DRK48C（MIUI 桌面，Android 16）上验证通过。

## 为什么不能直接伪造

一个有效的微信公众号桌面图标必须同时具备：

```text
1. 桌面 launcher 记录
2. 微信内部 shortcut_id / 映射
3. Chat_User=gh_... 对应的公众号 ID
```

只复制 `Chat_User` 或写 launcher/微信数据库，微信内部没有映射，图标仍然无效。
因此唯一安全路径是让微信自己执行“添加到桌面”。

## 安全前提

每次操作前确认设备：

```bash
ADB=/path/to/adb
$ADB devices -l
```

只操作确认的目标设备；出现 `unauthorized` 让用户点允许，`offline` 重插 USB。
禁止 `pm clear`、`rm`、改 SQLite、伪造 ShortcutInfo、批量删除快捷方式。

## 只读检查既有快捷方式

微信屏蔽 `uiautomator dump`，但可以点击图标后读 Activity/Fragment 参数：

```bash
# 点击目标图标（坐标以实际 dump 为准）
adb shell input tap <x> <y>
sleep 2
adb shell dumpsys activity -p com.tencent.mm activities > /tmp/mm.txt
grep -n -E 'Chat_User|mArguments=Bundle|ChattingUIFragment' /tmp/mm.txt
```

看到类似：

```text
mArguments=Bundle[{Chat_User=gh_0b101c0f2eb3, ...}]
```

即确认是微信公众号快捷方式。

## 新建公众号桌面图标的官方流程

微信界面屏蔽 UI dump，但截图可用。用 macOS Vision OCR 定位按钮。

### 1. OCR 脚本

将 `scripts/ocr_wechat.swift` 保存到本 skill 的 `scripts/` 目录后运行：

```bash
adb exec-out screencap -p > /tmp/screen.png
swift scripts/ocr_wechat.swift /tmp/screen.png
```

输出格式：

```text
x,y widthxheight<TAB>识别文本
```

### 2. 打开微信

微信可能在桌面文件夹内，先打开文件夹再点微信：

```bash
# 打开文件夹（坐标以实际 dump 为准）
adb shell input tap 181 1609
sleep 1.5
adb shell uiautomator dump /sdcard/folder.xml
adb pull /sdcard/folder.xml /tmp/folder.xml
# 找到“微信”图标后点击
adb shell input tap 313 1327
```

### 3. 进入搜索

微信主界面顶部右侧搜索图标（OCR 常显示为 `Q`）：

```bash
adb shell input tap 972 210
sleep 2
```

### 4. 搜索公众号

`adb shell input text` 不支持中文，有两种搜索方式：

#### 方式 A：拼音搜索（无需额外安装）

```bash
# 点搜索输入框
adb shell input tap 500 240
# 量子位 = liangziwei
adb shell input text 'liangziwei'
sleep 2
```

OCR 查看联想结果，点击目标公众号。适合能通过拼音联想的公众号；搜不到时换方式 B 或认为该号可能已失效。

#### 方式 B：ADBKeyBoard 中文输入（推荐，支持直接搜中文）

安装并启用 ADBKeyBoard：

```bash
# 下载 APK（仓库内文件名是 ADBKeyboard.apk，注意大小写）
# 安装失败 INSTALL_FAILED_USER_RESTRICTED 时，让用户允许 USB 安装后重试
adb install -r /tmp/ADBKeyBoard.apk

# 启用并设为当前输入法
adb shell ime enable com.android.adbkeyboard/.AdbIME
adb shell ime set com.android.adbkeyboard/.AdbIME
```

输入中文：

```bash
# 清空搜索框
adb shell am broadcast -a ADB_CLEAR_TEXT

# 用 base64 发送中文，避免 shell 编码问题
B64=$(printf '%s' '未来计算机二级Office' | base64)
adb shell am broadcast -a ADB_INPUT_B64 --es msg "$B64"
```

用完恢复原输入法：

```bash
adb shell ime set com.sohu.inputmethod.sogou.xiaomi/.SogouIME
```

注意：ADBKeyBoard 安装后默认输入法会变成它，必须恢复原 IME，否则手机正常键盘不可用。

### 5. 清空搜索框与切换筛选

如果搜索框里有文字，**直接点右侧的叉号 `x` 清空**，不需要返回：

```bash
# x 按钮位置以 OCR 为准，一般在搜索框右侧
adb shell input tap 868 178
```

清空后重新输入。

如果搜索结果没有直接显示目标公众号，**筛选行可以横向滑动**，找到“账号”分类：

```bash
# 小幅向左滑动，露出“账号”（不要大幅滑，否则会滑过头）
adb shell input swipe 700 370 500 370 200
# 然后点击“账号”
adb shell input tap 90 386
```

注意：大幅左滑可能直接滑过“账号”露出“划线”，此时再小幅右滑回来即可。

### 6. 进入公众号主页

在搜索结果中点击“关注的公众号”下方的公众号名称，或在“账号”筛选结果中点击目标公众号。

### 7. 关注公众号（如未关注）

如果公众号主页显示“关注服务号 / 关注公众号”，需要先关注：

```bash
# 点击“关注服务号/关注公众号”按钮（坐标以 OCR 为准）
adb shell input tap 608 1265
sleep 2
```

关注后微信**通常会直接进入该公众号的聊天界面**，不会再停留在简介页。

### 8. 从聊天界面回到简介页

在聊天界面**不要点标题**（标题点击无效），要点**右上角的头像**才能进入公众号简介页：

```bash
# 点右上角头像（坐标以 OCR 为准，一般在右上角约 1100,210）
adb shell input tap 1100 210
sleep 2
```

进入简介页后，再点右上角“•••”。

### 9. 找到“添加到桌面”

已验证路径：

```text
公众号简介页右上角“•••”
→ “设置”
→ “添加到桌面”
```

```bash
# 点右上角“•••”
adb shell input tap 1098 210
sleep 2
# 点“设置”
adb shell input tap 610 1829
sleep 2
# 点“添加到桌面”
adb shell input tap 226 1052
```

注意：不同公众号设置页中“添加到桌面”的 y 坐标可能不同（见过 1017 和 1221 两种），每次以 OCR 实际位置为准。

出现“已添加”提示即成功；有时提示很快消失，也可以直接回桌面确认图标是否出现。

### 10. 验证新图标

返回桌面找到新图标，点击后检查 `Chat_User`：

```bash
adb shell input keyevent 3
adb shell uiautomator dump /sdcard/desktop.xml
adb pull /sdcard/desktop.xml /tmp/desktop.xml
# 找到新图标坐标后点击
adb shell input tap <x> <y>
sleep 2
adb shell dumpsys activity -p com.tencent.mm activities > /tmp/verify.txt
grep -n -E 'Chat_User' /tmp/verify.txt
```

`Chat_User` 与目标公众号 `gh_...` 一致即成功。

## 常见坑（本次实测）

1. **ADB 安装 APK 可能被 MIUI 拦截**：`INSTALL_FAILED_USER_RESTRICTED` 时让用户允许 USB 安装后重试，通常第二次能成功。
2. **安装 ADBKeyBoard 后必须恢复原输入法**：否则手机正常键盘不可用。
3. **关注公众号后会自动进入聊天界面**：此时点标题无效，要点右上角头像回到简介页。
4. **“添加到桌面”的 y 坐标不固定**：同一台手机上不同公众号见过 `1017` 和 `1221`，必须用 OCR 实时确认。
5. **“已添加”提示可能不出现或一闪而过**：不要只依赖 toast，直接回桌面搜索新图标确认。
6. **拼音搜不到不一定是操作错误**：公众号可能已失效/改名/未收录，可跳过并记录。
7. **搜索框残留旧文字**：用 ADBKeyBoard 的 `ADB_CLEAR_TEXT` 清空，或直接点搜索框右侧的 `x`，不要靠多次 DEL。
8. **停在上一账号的设置页**：按返回回到该公众号主页，右上角搜索图标 `Q` 可直接进入搜索，不必退回微信主界面。
9. **搜索结果默认“全部”可能不显示公众号**：搜索框下方的筛选行可以横向滑动，找到“账号”分类后再点目标公众号。
10. **输入中文后先 OCR 确认搜索框文字**：如果旧文字没清干净，容易误以为输入错误；确认显示正确后再搜索。
11. **账号筛选也找不到时不要反复试**：公众号可能已失效/改名/未收录，直接跳过并记录，继续下一个。
12. **批量连续添加时不需要回桌面验证**：添加完一个后继续在微信里搜索下一个，最后再统一核对。
13. **如果微信图标已经移到目标页**：直接点微信图标打开，不需要再通过文件夹找微信。
14. **搜索优先级：公众号 > 视频号 > 小程序**：账号筛选里优先点“服务号/公众号”；小程序先排除（添加方式不同），视频号可尝试但优先级低于公众号。
15. **账号筛选里点“不限”往往能让公众号显示在最上面**：“公众号”子筛选有时点击后界面不变，不如直接点“不限”。
16. **Excel 名称可能是小程序/视频号**：例如“会计考试GO”实际是小程序；小程序先排除，视频号可尝试但优先级低于公众号。
17. **筛选行滑动要小幅**：大幅左滑会滑过“账号”露出“划线”，需要再小幅右滑回来；推荐小幅左滑 `700→500`。
18. **不要用一条 `adb shell` 串联“点输入框 + ADB_CLEAR_TEXT + 输入广播”**：快速合并命令会导致中文输入不稳定（出现旧文字/错误文字）；应分步执行，可以缩短 sleep，但不要合并广播输入。
19. **点“账号”后，第一个结果不一定是公众号**：可能是视频号/小程序，公众号可能在下面。需要继续向下找，优先找带“公众号/服务号/媒体”标签的结果。
20. **“添加到桌面”的 y 坐标还见过 `812`**：目前已知有 `812`、`1017`、`1221`、`1360` 四种，必须 OCR 确认。
21. **输入后直接点顶部“搜索”按钮**（约 `1040,200`），不要点键盘搜索键；ADBKeyBoard 下键盘搜索键可能不触发。
22. **如果搜索后停在“搜索内容 / 最近在搜”**：说明搜索没触发，点顶部“搜索”即可。
23. **有些视频号右上角“•••”没有“设置”**：这种视频号无法添加到桌面，直接跳过。
24. **如果进入的是视频号资料页但里面有“公众号：xxx”入口**：先点该入口进入真正的公众号设置页，再找“添加到桌面”。
25. **公众号名称太长时可能被 OCR 漏掉**：账号列表第一项可能是公众号，但名称被截断/遮挡导致 OCR 识别不到，脚本可能误选下面的视频号；遇到“视频号资料页且没有设置”时，应回退检查上方是否有被截断的公众号，或手动处理。
26. **公众号名称不全时使用模糊匹配**：OCR 只识别到部分名称时，用名称的前缀/关键字匹配（例如“大众新闻-大众日报”用“大众新闻”或“大众日报”），不要要求完整名称完全一致。
27. **模糊匹配后必须二次验证**：模糊匹配只用于“找候选”，不能直接确认。进入资料页后必须核对完整名称、主体/公司名、简介、gh_ ID 或 URL/biz；验证不通过就不添加，避免匹配到名称前缀相同的其他账号。
28. **已关注的公众号直接点右上角“•••”**：资料页显示“已关注”时，不需要再点“关注”，直接进入“••• → 设置 → 添加到桌面”。

## 已知限制

- **MIUI 通过 ADB 模拟“长按拖动创建文件夹”目前不可靠**：`input draganddrop`、`motionevent`、先进入编辑模式再拖动等方式都未能稳定创建文件夹；如果用户需要建文件夹，建议优先手动操作或改用其他自动化方案。
- ADB 适合“微信官方添加到桌面”的单图标新增；桌面布局的大规模拖拽整理仍以人工或专门 UI 自动化为宜。
- **小程序优先级最低，但会尝试添加**：小程序添加到主页方式与公众号不同，走专用流程；视频号优先级高于小程序，但低于公众号。

## 跨设备适配

以后可能连接不同品牌/尺寸/桌面布局的手机，必须注意：

- **不要套用固定坐标**：屏幕分辨率、密度、微信版本变化都会改变坐标；所有按钮位置必须通过 OCR 实时获取。
- **ADB 路径、serial、OCR 脚本可通过环境变量覆盖**：
  ```bash
  ADB_PATH=/path/to/adb \
  ANDROID_SERIAL=<新serial> \
  OCR_SCRIPT=/path/to/ocr_wechat.swift \
  python3 scripts/batch_add_wechat.py 公众号1 公众号2
  ```
- **桌面品牌/布局差异**：微信图标可能不在当前手机的文件夹/页面；先 `uiautomator dump` 扫描桌面，找到微信图标后再点击，不要假设固定路径。
- **微信内部布局差异**：不同微信版本中“账号”“关注”“添加到桌面”的位置和文案可能不同，必须以 OCR 实际结果为准。
- **“添加到桌面”入口差异**：部分机型/版本可能没有该入口，或入口位置不同；找不到就跳过并记录。
- **脚本中的默认坐标只是当前测试机的值**：换机后优先改用 OCR 定位，或更新脚本中的默认坐标。

## 小程序添加流程

小程序也考虑，但优先级最低。进入小程序后：

```text
右上角“•••”
→ 底部找到“转发给朋友”那一行
→ 向左滑动该行
→ 右侧出现“添加到桌面/添加到”
→ 点击“添加到”
→ 点击右下角返回，继续下一个
```

注意事项：

- 小程序的“添加到桌面”入口在“转发给朋友”行的滑动扩展里，不在“设置”里；
- 添加完成后右下角返回即可继续下一个；
- 如果小程序右上角“•••”没有“转发给朋友”或滑动后没有“添加到”，则跳过。

## 注意点

- 微信 `uiautomator dump` 返回空节点，不要依赖 UI XML 操作微信内部。
- 坐标会因机型/微信版本变化，每次先 OCR 确认。
- 若 MIUI 弹出“创建桌面快捷方式”权限，需要用户在手机上点允许。
- 只允许微信自己注册快捷方式；不要写数据库、不要伪造 shortcut_id。
