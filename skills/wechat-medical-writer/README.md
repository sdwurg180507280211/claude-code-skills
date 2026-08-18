# wechat-medical-writer

医学类微信公众号 / 服务号的**轻量领域适配与编排 Skill**。

它不自己维护一套文章模板、研究模式、Claim Ledger 或发布代码，而是把职责拆清楚：

```text
医学领域上下文 + 必要医学约束
        ↓
【必须】content-research-writer
负责主题 → 研究 → 引用 → 高质量文章
        ↓
医学引用完整性检查
        ↓
可选：Viral Writer
只做表达/标题/节奏润色，不改变医学事实
        ↓
用户需要时才进入苍何下游
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

## Writer handoff

`wechat-medical-writer` 不再把 `content-research-writer` 当成“有就用”的建议，而是把通用写作阶段强制交给它。

Handoff 时把当前已经知道的主题、受众、目标、篇幅/形式、用户资料、参考样稿、风格要求和医学约束一起传给主 Writer；已经明确的信息不要重复问。

用户要求“直接成稿 / 一口气完成”时，可以让主 Writer 在同一轮连续完成大纲、研究、草稿、引用检查和最终润色，不需要人为停在每个协作步骤。

如果运行环境确实缺少 `content-research-writer`，停止正文并提示补装；不要悄悄切换成自制 fallback Writer。

## 医学证据边界

面向公开发布的医学文章，即使用户没有额外说“帮我核验”，具体医学数字、指南/共识推荐、疗效/安全性、适应证、监管状态和其他可能影响临床判断的关键结论也应能回到可追溯来源。

成稿前检查：

- 正文引用与 Reference 一一对应；
- 具体数字可以定位到真实来源；
- DOI / PMID / 作者 / 年份 / 期刊等不凭记忆补齐；
- 来源只支持“相关/提示”时，不升级为“证实/导致”。

用户明确要求“只根据我给的资料写、不做外部核验”时可以遵从，但最终稿必须说明该来源边界。

完整规则见 `references/medical-constraints.md`。

## 参考文章

用户提供优秀公众号文章时，把它作为写作风格、结构、信息密度和完成度参考，不把其中医学数字和文献自动当成已核验事实，也不把样稿结构固化成永久模板。

## Upstream

- 主 Writer：`content-research-writer`（CommandCodeAI/agent-skills）
- 可选传播润色：`Viral Writer`（仅表达层）
- 配图/排版/发布：苍何 `canghe-article-illustrator`、`canghe-markdown-to-html`、`canghe-post-to-wechat`

`content-research-writer` 已按上游 MIT License 放入本仓库的 `skills/content-research-writer/`，并加入 `utility-skills` bundle。该 vendored Skill 不做医学魔改；本地完整性由 `UPSTREAM.lock.json` 保护。

苍何不属于纯写作的安装前置条件。只有用户要求配图、排版或发布时才做 preflight；若未安装，使用：

```text
/plugin marketplace add freestylefly/canghe-skills
/plugin install content-skills@canghe-skills
/plugin install utility-skills@canghe-skills
```

医学配图继续受 `medical-constraints.md` 约束：数据图不补造数字，机制图不把推测画成确定因果，真实产品/器械优先使用官方素材。

具体来源、固定版本和职责见 `references/upstreams.md`。

## 仓库边界

原始医学 ZIP/PPT/PDF、内部培训材料、未公开研究、患者资料和运行时文章都不进入本公共仓库。

本 Skill 自身只保留领域定义、医学约束和 upstream 编排说明；`content-research-writer` 作为独立、带许可证、来源记录和完整性锁的 upstream 副本维护。
