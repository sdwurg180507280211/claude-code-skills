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

这是默认且必需的“主题 → 高质量文章”上游。`wechat-medical-writer` 只向它补充医学领域上下文和 `medical-constraints.md`，不改写它的写作流程。

### Handoff

医学 Skill 在开始大纲、研究或正文前，把当前已知的主题、受众、目标、篇幅/形式、用户资料、参考样稿、风格要求、医学领域上下文和医学约束一次性传给 `content-research-writer`。

已知信息不重复问。用户要求“一口气成稿”时，仍使用主 Writer 的原生步骤，只是把大纲 → 研究 → 草稿 → 引用检查 → 最终润色连续执行，不要求用户在每个协作节点停下来确认。

如果运行时无法调用主 Writer，停止正文创作并报告依赖问题；不要让医学 Skill 自己承担一套隐形 fallback Writer。

### 本仓库的安装方式

由于该 upstream 目前不在用户可用的插件市场中，本仓库按其 MIT License 将已审计版本 vendor 到：

```text
skills/content-research-writer/
├── SKILL.md
├── LICENSE
├── UPSTREAM.md
└── UPSTREAM.lock.json
```

并将它和 `wechat-medical-writer` 一起加入 `utility-skills` bundle。

因此安装：

```text
/plugin install utility-skills@my-skills
```

即可同时获得主 Writer 与医学适配层。

这不是 fallback Writer，也不是本仓库重新实现的 Writer；`SKILL.md` 不加入医学特有逻辑，`UPSTREAM.md` 记录固定版本与同步规则，`UPSTREAM.lock.json` 锁定本地 vendored 内容，`LICENSE` 保留上游 MIT 许可和版权声明。

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

### Preflight

纯研究/写作任务不依赖苍何，不要因为下游未安装而阻塞正文。

只有用户要求配图、排版或上传时才检查苍何。缺少时给出其标准安装命令：

```text
/plugin marketplace add freestylefly/canghe-skills
/plugin install content-skills@canghe-skills
/plugin install utility-skills@canghe-skills
```

其中 `canghe-article-illustrator`、`canghe-post-to-wechat` 属于内容生产链，`canghe-markdown-to-html` 属于 utility 链。安装后调用 upstream，不在本仓库补写替代实现。

配图时继续叠加 `medical-constraints.md` 中的数据图、机制图和产品素材约束。苍何负责“如何配图”，医学 Skill 只负责“哪些医学事实不能被图像生成过程改写或补造”。

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
【MANDATORY】content-research-writer
        ↓
医学引用完整性检查
        ↓
可选 Viral Writer 表达润色
        ↓
用户要求下游时才做苍何 preflight
        ↓
可选 canghe-article-illustrator
        ↓
canghe-markdown-to-html
        ↓
canghe-post-to-wechat
```

原则不是“所有 upstream 都不能复制”，而是：优先直接依赖；只有在**实际安装不可达且许可证允许**时，才保留一个明确标注来源、固定版本、许可证完整、尽量不修改且受完整性锁保护的 vendored 副本。当前只对 `content-research-writer` 使用这一例外。
