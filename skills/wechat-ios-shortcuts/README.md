# WeChat iOS Shortcuts Skill

把微信公众号主页或文章 URL 批量生成 iPhone/iPad 可安装的 `.mobileconfig`，通过 Apple Web Clip 在主屏幕创建公众号图标。

## 和另外两个微信 Skill 的区别

```text
wechat-account-bookmarks
公众号身份 / biz / 文章 URL → Edge / Chrome 书签

wechat-android-shortcuts
ADB + 微信 UI → Android 微信官方“添加到桌面”

wechat-ios-shortcuts
名称 + URL → Apple Web Clip → .mobileconfig → iOS 主屏幕图标
```

## 快速开始

```bash
cd skills/wechat-ios-shortcuts
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python3 scripts/generate_webclips.py \
  --input /path/to/wechat_accounts.csv \
  --output output/wechat-ios-webclips.mobileconfig
```

如果输入是 `wechat-account-bookmarks` 生成的 `wechat_accounts.csv`，默认会识别 `target_url` 作为最终跳转 URL。

普通 CSV 也可以：

```csv
公众号名称,target_url
量子位,https://mp.weixin.qq.com/s/example1
财新,https://mp.weixin.qq.com/s/example2
```

也支持 `.xlsx/.xlsm`：

```bash
python3 scripts/generate_webclips.py \
  --input accounts.xlsx \
  --sheet 前面区域 \
  --name-column 快捷方式名称 \
  --url-column URL \
  --output output/wechat.mobileconfig
```

## 可选 PNG 图标

输入可以增加图标路径：

```csv
公众号名称,target_url,图标路径
量子位,https://mp.weixin.qq.com/s/example1,icons/量子位.png
```

相对路径以输入文件目录为基准。图标会作为 `Icon` 数据嵌入 Web Clip payload。

## 配置项

```text
--profile-name      iOS 设置中显示的描述文件名称
--profile-id        PayloadIdentifier
--organization      PayloadOrganization
--fullscreen        FullScreen=true
--non-removable     IsRemovable=false
```

默认行为更适合个人设备：

```text
FullScreen=false
IsRemovable=true
Precomposed=true
IgnoreManifestScope=false
```

## 输出结构

一个 `.mobileconfig` 内可包含多个 `com.apple.webClip.managed` payload。每个有效输入名称生成一个主屏幕 Web Clip。

同时生成：

```text
wechat-ios-webclips.summary.json
```

用于查看成功数量、跳过记录、重复名称和最终 URL。

## 在 iPhone 上安装

把 `.mobileconfig` 发送到 iPhone（例如文件、邮件或网页下载），然后按 iOS 提示进入“设置”确认安装。个人设备不能由本 Skill 静默安装；本 Skill 只负责生成配置描述文件。

移除整个配置描述文件时，其中创建的 Web Clip 也会随之移除。默认每个 Web Clip 本身也允许用户从主屏幕删除。

## Apple 官方资料

- Web Clip payload: https://developer.apple.com/documentation/devicemanagement/webclip
- Configuration Profile installation: https://support.apple.com/102400

## 当前边界

- 不负责解析公众号名称到 URL；推荐先用 `wechat-account-bookmarks` 得到 `target_url`。
- 不保证 `profile_ext` 公众号主页在所有 iOS/微信环境可打开；有稳定文章 URL 时可以直接使用文章。
- 不尝试生成没有 HTTP/HTTPS 跳转地址的小程序原生入口。
- 不控制 iPhone 微信 UI，不使用 XCTest/WebDriverAgent。
- 不绕过配置描述文件安装确认或 MDM 权限。
