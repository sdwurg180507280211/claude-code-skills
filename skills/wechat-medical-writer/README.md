# wechat-medical-writer

医学类微信公众号 / 服务号的**轻量领域适配与编排 Skill**。

它不再自己维护一套文章模板、研究模式、Claim Ledger 或发布代码，而是把职责拆清楚：

```text
医学领域上下文 + 必要医学约束
        ↓
content-research-writer
负责主题 → 研究 → 引用 → 高质量文章
        ↓
可选：Viral Writer
只做表达/标题/节奏润色，不改变医学事实
        ↓
canghe-article-illustrator
canghe-markdown-to-html
canghe-post-to-wechat
```

## 当前领域方向

用户提供的医学 ZIP/PPT 只用于定义后续内容方向或作为某次写作资料，**不决定固定文章结构**。

当前方向包括：

- 女性健康 / 妇科
- HPV 感染与持续感染
- 宫颈癌筛查与防治
- LSIL / HSIL
- CIN2 / CIN3
- 阴道镜 / 病理 / 风险分层
- 生育需求与宫颈功能保护
- PDT / HAL-PDT

详细 taxonomy：`references/domains/cervical-health.md`。

## 参考文章

用户提供优秀公众号文章时，把它作为写作风格、结构、信息密度和完成度参考，不把其中医学数字和文献自动当成已核验事实，也不把样稿结构固化成永久模板。

## Upstream

- 主 Writer：`content-research-writer`（CommandCodeAI/agent-skills）
- 可选传播润色：`Viral Writer`（仅表达层）
- 配图/排版/发布：苍何 `canghe-article-illustrator`、`canghe-markdown-to-html`、`canghe-post-to-wechat`

`content-research-writer` 目前已按上游 MIT License **原样放入本仓库**的 `skills/content-research-writer/`，并加入 `utility-skills` bundle，因此安装本仓库的 utility bundle 时会同时得到医学编排层和主 Writer。该 vendored Skill 不做医学魔改；医学约束仍只存在于 `wechat-medical-writer`。

具体来源、固定版本和职责见 `references/upstreams.md`。

## 仓库边界

原始医学 ZIP/PPT/PDF、内部培训材料、未公开研究、患者资料和运行时文章都不进入本公共仓库。

本 Skill 自身只保留领域定义、医学约束和 upstream 编排说明；`content-research-writer` 作为独立、带许可证与来源记录的 upstream 副本维护。
