---
name: wechat-ios-shortcuts
description: 将微信公众号主页或文章 URL 批量生成 iPhone/iPad 可手动安装的 Web Clip 配置描述文件（.mobileconfig），让公众号名称以主屏幕图标形式出现。可直接读取 wechat-account-bookmarks 输出的 wechat_accounts.csv，也可读取普通 CSV/XLSX；适用于“iPhone 批量创建公众号桌面图标”“把公众号文章放到 iOS 主屏幕”“生成微信 Web Clip 配置描述文件”等任务。不控制微信 App、不绕过 iOS 权限、不自动安装描述文件。
---

# 微信 iOS 主屏幕快捷方式

## 定位

本 Skill 负责把已经确定的可点击 URL 转成 Apple 官方 Web Clip 配置描述文件：

```text
CSV / XLSX / wechat_accounts.csv
→ 名称 + target_url / URL
→ com.apple.webClip.managed
→ .mobileconfig
→ 用户在 iPhone 设置中确认安装
→ 主屏幕出现图标
```

它不使用 ADB，也不通过 UI 自动化逐个操作微信。Android 真机微信“添加到桌面”使用 `wechat-android-shortcuts`；公众号身份、文章 URL、biz 与浏览器书签使用 `wechat-account-bookmarks`。

## Apple 机制

Web Clip payload 类型固定为：

```text
com.apple.webClip.managed
```

每个条目至少包含：

```text
Label
URL
PayloadIdentifier
PayloadUUID
PayloadType
PayloadVersion
```

可选本地 PNG 图标会嵌入 `Icon` 数据。默认 `IsRemovable=true`、`FullScreen=false`、`Precomposed=true`。

## 推荐工作流

已有 `wechat-account-bookmarks` 输出时直接使用：

```bash
python3 scripts/generate_webclips.py \
  --input ../wechat-account-bookmarks/output/wechat_accounts.csv \
  --output output/wechat-ios-webclips.mobileconfig
```

脚本会优先自动识别：

```text
名称：current_name / original_name / 公众号名称 / 快捷方式名称
URL：target_url / URL / url / 链接
图标：icon_path / 图标路径 / 头像路径（可选）
```

没有 `target_url` 的记录不会生成 Web Clip。

## 普通 Excel / CSV

最小输入：

```text
公众号名称,target_url
量子位,https://mp.weixin.qq.com/s/...
财新,https://mp.weixin.qq.com/s/...
```

Excel：

```bash
python3 scripts/generate_webclips.py \
  --input accounts.xlsx \
  --sheet 前面区域 \
  --name-column 快捷方式名称 \
  --url-column URL \
  --output output/wechat.mobileconfig
```

## 图标

可增加 PNG 路径列：

```text
公众号名称,target_url,图标路径
量子位,https://mp.weixin.qq.com/s/...,icons/量子位.png
```

相对路径以输入文件所在目录为基准。脚本只接受 PNG，文件需不超过 1 MB。未提供图标时仍生成 Web Clip，由 iOS 使用默认图标表现。

## 输出

```text
wechat-ios-webclips.mobileconfig
wechat-ios-webclips.summary.json
```

`summary.json` 记录成功条目和跳过原因，例如：

```text
missing_name
missing_or_invalid_url
duplicate_name
```

## 安装

生成的 `.mobileconfig` 是未签名配置描述文件，需要用户主动在 iPhone/iPad 上确认安装。不要声称可以静默安装到个人 iPhone；只有设备管理场景才可能由 MDM 下发。

## 边界

- Web Clip 是 URL 主屏幕入口，不等同于微信原生 Android ShortcutInfo。
- 公众号主页 URL 是否能在 iOS 环境稳定打开取决于微信；文章 URL 通常更适合作为保底目标。
- 本 Skill 不负责发现公众号、不调用 `searchbiz/appmsgpublish`，也不处理微信频控。
- 小程序只有在已有稳定 HTTP/HTTPS 跳转 URL 时才能按 Web Clip 处理；不能凭名称生成原生小程序入口。
- 不自动安装描述文件，不绕过用户确认、MDM、系统安全限制。

## 验证

```bash
pip install -r requirements.txt
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts
```
