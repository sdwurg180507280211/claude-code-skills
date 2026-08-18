# Repository Guide

本仓库是自包含 Agent Skills 集合。

## 目录约定

- 每个 Skill 放在 `skills/<skill-name>/`。
- `SKILL.md` 必须存在，frontmatter 至少包含 `name` 与 `description`。
- 脚本、测试、示例、参考资料都放在对应 Skill 目录内。
- 不把运行结果、用户输入、Cookie、Token、session、二维码、缓存提交到仓库。

## 质量要求

1. Skill 的触发描述要具体，避免劫持无关任务。
2. 优先成熟依赖和简单实现，不为了未来功能增加额外兼容层。
3. 可确定验证的解析/转换能力应提供离线测试。
4. 新增或删除 Skill 时同步更新 `README.md`、`.claude-plugin/marketplace.json` 和 `CHANGELOG.md`。
5. 提交前运行 `python3 scripts/validate_skills.py`，并运行对应 Skill 的测试。

## WeChat Skills

- `wechat-account-bookmarks` 只负责微信公众号身份 / 文章 / `biz` 到 Edge / Chrome 书签的编排与输出；微信侧复杂发现和文章解析优先复用固定版本的苍何上游 Skill。只使用正常扫码登录与公开可访问数据，不绕过验证码、登录限制、访问控制、频率限制或微信风控。
- `wechat-android-shortcuts` 只负责 Android 真机上的微信“添加到桌面”自动化；使用 ADB + OCR 操作官方 UI，不修改微信数据库、不伪造 ShortcutInfo，不与其他微信 Skill 互相 import。
- `wechat-ios-shortcuts` 只负责名称 + 已知 HTTP/HTTPS URL 到 Apple Web Clip `.mobileconfig` 的转换；不发现公众号、不控制微信 App、不静默安装配置描述文件。个人 iPhone/iPad 安装必须由用户确认，MDM 下发不属于当前实现。
- `wechat-medical-writer` 只负责医学公众号/服务号文章的资料编排、证据追溯和写作，不复制公众号发布实现。默认用户医学资料优先，关键疗效/安全性/适应证/监管/指南/比较性表述必须进入 Claim Ledger。
- 四个微信 Skill 通过 Markdown、CSV/XLSX、`target_url`、Claim Ledger 等文件/数据契约松耦合，不直接互相 import。
- Android 脚本不得提交开发机绝对路径、固定设备 serial、固定用户输入法；设备和工具路径通过自动发现或环境变量提供，临时切换输入法后必须恢复运行前的默认输入法。
- 医学 Skill 不得提交用户上传的原始 ZIP/PPT/PDF、内部培训材料、患者资料、未公开研究、真实 Claim Ledger 或文章运行产物。仓库内只保存通用规则、模板、高层领域 taxonomy 和离线校验逻辑。
- 医学写作不得把课件中的推广语直接升级为医学事实；来源不足时标记待核验，不虚构指南、论文、样本量、统计结果或监管状态。
