# Apple Web Clip 参考

本 Skill 使用 Apple Device Management 的 Web Clip payload，不自己定义 iOS 主屏幕协议。

## 官方文档

- Web Clip payload: https://developer.apple.com/documentation/devicemanagement/webclip
- iPhone 安装配置描述文件: https://support.apple.com/102400

## 本 Skill 使用的字段

```text
PayloadType = com.apple.webClip.managed
Label       = 主屏幕显示名称
URL         = 点击后打开的 HTTP/HTTPS URL
Icon        = 可选 PNG 二进制数据
FullScreen  = 是否以 Web App 全屏打开
IsRemovable = 是否允许单独删除 Web Clip
Precomposed = 是否禁止系统给图标增加高光效果
```

顶层 profile：

```text
PayloadType = Configuration
PayloadContent = [多个 Web Clip payload]
```

Apple 文档允许 iOS 手动安装 Web Clip 配置描述文件，也允许一个 profile 中包含多个 Web Clip payload。

## 安装边界

个人设备手动安装需要用户确认。本 Skill 只生成 `.mobileconfig`，不尝试静默安装。已纳入 MDM 的设备可由设备管理系统下发，但 MDM 下发不属于本 Skill 当前实现。
