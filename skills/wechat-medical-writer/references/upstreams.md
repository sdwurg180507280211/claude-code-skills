# Upstreams

本 Skill 不复制成熟 Writer 或公众号发布实现，而是把它们作为 upstream 使用。

## 1. 主 Writer：content-research-writer

来源：`CommandCodeAI/agent-skills`

路径：`skills/content-research-writer/SKILL.md`

已审计版本：`f490dd9016f2729311e90f317dcb6c98be1a1500`

职责：

- 主题理解；
- 协作式大纲；
- 资料研究；
- 引用管理；
- Hook 优化；
- 正文创作；
- 分节反馈；
- 最终润色；
- 保持用户指定的语气 / 风格。

这是默认的“主题 → 高质量文章”上游。`wechat-medical-writer` 只向它补充医学领域上下文和 `medical-constraints.md`，不复制它的写作流程。

如果未安装，应提示用户安装该 upstream；不要写一套本地 fallback Writer。

## 2. 可选传播润色：Viral Writer

来源：`nashsu/Viral_Writer_Skill`

已审计版本：`1c76f891fb928ceb22fd101044d100d759f8cee5`

用途仅限：

- 标题方案；
- 开头吸引力；
- 段落节奏；
- 表达可读性；
- 公众号传播表达。

不让它负责医学事实生产、医学研究、数字、引用、指南或监管结论。

当前仓库元数据未显示明确 License，因此本仓库不复制或 vendor 其内容；仅在用户明确需要且运行环境已经安装时调用。

## 3. 微信公众号生产链：苍何

来源：`freestylefly/canghe-skills`

已审计版本：`dd0bf355955b4c82b764740b4183c86a72ba0e0c`

使用：

```text
canghe-article-illustrator
canghe-markdown-to-html
canghe-post-to-wechat
```

职责：

- 文章正文配图（按需）；
- Markdown → 微信公众号 HTML；
- 标题、摘要、封面等发布前处理；
- 微信 API / Chrome 路径上传到公众号草稿箱。

本仓库不复制苍何代码，也不维护另一套微信发布实现。

当前仓库元数据未显示明确 License，因此保持“调用 upstream，不复制代码”的边界。

## 4. 不作为默认主链：wechat-article-writer

来源：`xstongxue/best-skills`。

它提供通用公众号写作、配图和上传，但与苍何生产链存在明显职责重叠，而且默认研究逻辑更偏通用自媒体 / 技术内容。

因此当前架构不把它作为必需依赖。若用户未来明确指定使用，可单独评估，而不是同时维护两套发布链。

## 5. 编排原则

```text
用户主题 / 私有资料 / 参考样稿
        ↓
wechat-medical-writer
医学领域上下文 + 必要医学约束
        ↓
content-research-writer
        ↓
可选 Viral Writer 表达润色
        ↓
可选 canghe-article-illustrator
        ↓
canghe-markdown-to-html
        ↓
canghe-post-to-wechat
```

任何一步已有成熟 upstream 时，不在本 Skill 内重复实现。
