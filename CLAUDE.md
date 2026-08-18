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
6. 默认不复制大型通用 upstream；若 upstream 实际安装不可达、许可证明确允许且是当前链路必需，可保留受控 vendored 副本，但必须附许可证、固定版本、来源说明和完整性锁，避免长期魔改分叉。

## WeChat Skills

- `wechat-account-bookmarks` 只负责微信公众号身份 / 文章 / `biz` 到 Edge / Chrome 书签的编排与输出；微信侧复杂发现和文章解析优先复用固定版本的苍何上游 Skill。只使用正常扫码登录与公开可访问数据，不绕过验证码、登录限制、访问控制、频率限制或微信风控。
- `wechat-android-shortcuts` 只负责 Android 真机上的微信“添加到桌面”自动化；使用 ADB + OCR 操作官方 UI，不修改微信数据库、不伪造 ShortcutInfo，不与其他微信 Skill 互相 import。
- `wechat-ios-shortcuts` 只负责名称 + 已知 HTTP/HTTPS URL 到 Apple Web Clip `.mobileconfig` 的转换；不发现公众号、不控制微信 App、不静默安装配置描述文件。个人 iPhone/iPad 安装必须由用户确认，MDM 下发不属于当前实现。
- `wechat-medical-writer` 是薄医学领域适配/编排层，不自己定义通用文章结构、标题方法、研究模式、固定模板或发布实现。用户医学 ZIP/PPT 只用于定义内容方向或作为当次资料。
- 医学主题到成稿必须 handoff 给 `content-research-writer`。由于该 upstream 在用户可用的插件市场不可达，本仓库按 MIT License 将已审计版本 vendored 为独立 `skills/content-research-writer/` 并加入 `utility-skills` bundle；不得在该 vendored `SKILL.md` 中加入医学特有逻辑。
- `content-research-writer` 的本地副本必须由 `UPSTREAM.lock.json` 锁定；`scripts/validate_skills.py` 会检查 Git blob 指纹，未同步更新 lock 的本地改动应直接失败。
- 如果运行环境只安装了 `wechat-medical-writer` 而缺少 `content-research-writer`，应提示安装同仓库主 Writer，不得悄悄实现 fallback Writer。
- Handoff 时把已知的主题、受众、目标、篇幅/形式、用户资料、参考样稿、风格要求和医学约束一次性传给主 Writer；已经知道的信息不要重复问。用户明确要求“一口气成稿”时，可让主 Writer连续执行原生的大纲、研究、草稿、引用检查和最终润色步骤。
- 面向公开发布的医学文章，关键数字、指南/共识推荐、疗效/安全性、适应证、监管状态和可能影响临床判断的事实默认要求可追溯来源；正文引用与参考文献在交付前必须闭环。只有用户明确要求“仅按提供资料、不做外部核验”时才允许限制在用户来源，并在成稿中说明该边界。
- `Viral Writer` 仅可作为用户明确要求时的可选表达润色层，不得修改或新增医学事实、数字、指南、适应证、监管状态或引用。
- 苍何不是纯写作的前置依赖。只有用户要求配图、Markdown → 微信 HTML、草稿箱上传时才检查并调用 `canghe-article-illustrator`、`canghe-markdown-to-html`、`canghe-post-to-wechat`；缺少时给出苍何标准安装方式，不自行实现替代版本。
- 医学配图的数据只能来自已经核验的正文来源；不得补造数字，不得把机制推测画成确定因果，真实产品/器械/包装优先使用用户提供的官方素材。
- 四个本仓库微信 Skill 保持独立，通过 Markdown、CSV/XLSX、`target_url` 等文件/数据契约松耦合，不直接互相 import。
- Android 脚本不得提交开发机绝对路径、固定设备 serial、固定用户输入法；设备和工具路径通过自动发现或环境变量提供，临时切换输入法后必须恢复运行前的默认输入法。
- 医学 Skill 不得提交用户上传的原始 ZIP/PPT/PDF、内部培训材料、患者资料或未公开研究。仓库只保存领域 taxonomy、必要医学约束和 upstream 编排说明。
- 用户提供的优秀公众号文章可以作为结构/文风/信息密度参考，但其医学结论和参考文献不能因为出现在样稿中就自动视为已核验事实；也不得把样稿结构固化为永久模板。
