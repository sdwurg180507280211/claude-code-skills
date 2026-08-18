# Reusable Upstream Skills

本文件只记录已经存在的成熟 Skill 及其职责边界。`wechat-medical-writer` 不复制、不改写这些 Skill 的方法论。

## 主题 / 资料 → 文章

### wechat-article-writer

Repository: `xstongxue/best-skills`

Path: `skills/wechat-article-writer/SKILL.md`

用途：公众号/自媒体全流程创作。它自己定义资料搜索、文章撰写、标题、排版建议、配图和可选上传流程。

规则：如果用户指定使用它，直接读取并遵循它自己的 `SKILL.md`；医学 Skill 只提供医学领域上下文和用户参考资料。

### Viral Writer

Repository: `nashsu/Viral_Writer_Skill`

Path: `SKILL.md`

用途：从主题或素材生成微信公众号、小红书、抖音等平台内容，并提供标题和配图指导。

规则：如果用户指定使用它，保持它原有创作流程，不在医学 Skill 中重新实现 11 个内容洞见维度或平台规范。

### content-research-writer

Repository: `CommandCodeAI/agent-skills`

Path: `skills/content-research-writer/SKILL.md`

用途：研究型长文的 outline、资料研究、引用、Hook、逐节反馈和最终润色。

规则：如果用户指定研究型写作或明确指定这个 Skill，直接使用它自己的流程；医学参考资料作为其 sources 输入的一部分。

## 配图 / 排版 / 微信公众号

### canghe-article-illustrator

Repository: `freestylefly/canghe-skills`

用途：文章配图。用户需要配图时直接使用该 Skill，不在本 Skill 中创建另一套插图流程。

### canghe-markdown-to-html

Repository: `freestylefly/canghe-skills`

用途：Markdown 转公众号 HTML 和主题排版。用户需要公众号排版时直接使用。

### canghe-post-to-wechat

Repository: `freestylefly/canghe-skills`

Path: `skills/canghe-post-to-wechat/SKILL.md`

用途：通过 API 或 Chrome 浏览器把文章保存到微信公众号草稿箱/执行其支持的发布流程。

规则：公众号凭证、标题/摘要/封面、API/浏览器方法等均按苍何 Skill 自己的规则执行，不在 `wechat-medical-writer` 重复实现。

## 选择原则

- 用户点名一个 Skill：使用用户指定的 Skill。
- 宿主环境已经明确路由到某个 Skill：遵循宿主路由结果。
- 多个写作 Skill 同时适用且没有明确选择：不要私自混合它们的流程。
- `wechat-medical-writer` 只向被选中的 Skill 提供：医学内容方向 + 当前用户参考资料。
