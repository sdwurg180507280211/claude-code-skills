# wechat-medical-writer

医学类微信公众号/服务号的**领域上下文与参考资料适配层**。

## 它是什么

当前服务号方向以女性健康、妇科和宫颈疾病为主，覆盖 HPV、HSIL、CIN2/CIN3、生育需求/生育力保护、PDT/HAL-PDT 等主题。

用户提供的医学 ZIP / PPT / PDF 等材料作为**参考资料**使用。它们可以为文章提供事实、术语、案例、研究线索和内容方向，但不负责决定文章编排，也不是唯一信息源。

## 它不是什么

本 Skill 不自己发明另一套：

- 文章结构
- 写作方法
- 标题/Hook 方法论
- 配图流程
- Markdown 排版
- 微信公众号上传/发布

这些能力直接复用现成 Skill，并遵循那些 Skill 自己的流程。

## 现成能力复用

当前明确支持的上游/下游包括：

```text
主题 / 参考资料
        ↓
现成写作 Skill
- wechat-article-writer
- Viral Writer
- content-research-writer
        ↓
文章成稿
        ↓
苍何现成 Skill（按用户需要）
- canghe-article-illustrator
- canghe-markdown-to-html
- canghe-post-to-wechat
```

具体来源和职责见 `references/upstreams.md`。

如果用户已经指定使用哪一个写作 Skill，就直接使用它；如果多个写作 Skill 同时可用且用户没有指定，本 Skill 不擅自把它们拼成新的工作流。

## 当前参考资料包

当前压缩包及其中课件只作为医学参考资料。仓库中只保留高层领域索引：

`references/domains/cervical-health.md`

原始 ZIP/PPT 不上传 GitHub。

## 私有资料

长期使用时可把资料放在仓库外，例如：

```text
~/medical-content-library/
└── cervical-health/
    ├── slides/
    ├── papers/
    ├── guidelines/
    └── notes/
```

如果资料已经作为当前会话附件上传，直接读取附件即可。
