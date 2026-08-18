# Upstreams

本 Skill 不重写成熟 Writer 或公众号发布实现，而是把它们作为 upstream 使用。

## 1. 主 Writer：content-research-writer

来源：`CommandCodeAI/agent-skills`

上游路径：`skills/content-research-writer/SKILL.md`

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

这是默认的“主题 → 高质量文章”上游。`wechat-medical-writer` 只向它补充医学领域上下文和 `medical-constraints.md`，不改写它的写作流程。

### 本仓库的安装方式

由于该 upstream 目前不在用户可用的插件市场中，本仓库按其 MIT License 将已审计版本**原样 vendor** 到：

```text
skills/content-research-writer/
├── SKILL.md
├── LICENSE
└── UPSTREAM.md
```

并将它和 `wechat-medical-writer` 一起加入 `utility-skills` bundle。

因此安装：

```text
/plugin install utility-skills@my-skills
```

即可同时获得主 Writer 与医学适配层。

这不是 fallback Writer，也不是本仓库重新实现的 Writer；`SKILL.md` 保持上游原文，`UPSTREAM.md` 记录固定版本与同步规则，`LICENSE` 保留上游 MIT 许可和版权声明。

如果用户只手工复制了 `wechat-medical-writer`，则还需要同时安装同仓库的 `content-research-writer`。

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

原则不是“所有 upstream 都不能复制”，而是：优先直接依赖；只有在**实际安装不可达且许可证允许**时，才保留一个明确标注来源、固定版本、许可证完整、尽量不修改的 vendored 副本。当前只对 `content-research-writer` 使用这一例外。
