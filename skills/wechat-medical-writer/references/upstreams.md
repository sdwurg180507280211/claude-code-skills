# Upstreams

本 Skill 不重写成熟 Writer、排版或公众号发布实现，而是把它们作为 upstream 使用。

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

## 3. 配图与发布：苍何

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
- 常规 Markdown → 微信公众号 HTML；
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

配图时继续叠加 `medical-constraints.md` 中的数据图、机制图和产品素材约束。苍何负责“如何配图”，医学 Skill 只负责“哪些医学事实不能被图像生成过程改写或补造”。

本仓库不复制苍何代码，也不维护另一套微信发布实现。

当前仓库元数据未显示明确 License，因此保持“调用 upstream，不复制代码”的边界。

## 4. 高级公众号布局：xiaohu-wechat-format

来源：`xiaohuailabs/xiaohu-wechat-format`

已审计版本：`dbddf0fd9c1189a6f3e0bec1bebb1b0e47e8ddf0`

当前仓库约 687 stars / 93 forks；Python 实现。它的定位与当前需求高度吻合：Markdown → 微信兼容 inline HTML，并支持大量主题与结构化容器。

### 值得复用的能力

- `:::dialogue[标题]`：把 `说话人：内容` 解析成左右交替的对话气泡；
- `:::intro`：文首导读块；
- gallery / stat / timeline / steps / compare / quote / byline / video 等容器；
- `interview` 等访谈主题；
- 85 套主题、画廊预览；
- 微信兼容的 inline style 输出；
- CJK 空格、中文标点和外链脚注处理。

这些能力适合“专家访谈、Q&A、圆桌、导语卡、总结卡、时间线”等普通 Markdown 很难表达的公众号布局。

### 当前限制

当前 `dialogue` 实现只支持：

```text
说话人文本 + 内容 + 左右交替气泡
```

代码中没有头像 / Logo 字段。因此对“左侧品牌 Logo + 右侧专家圆形头像”的参考样式只能做结构近似，不能宣称原生 1:1 复刻。

另外，`dialogue`、`intro` 等容器的部分样式直接写在 `scripts/format.py`，并非全部由主题 JSON 控制；想精确复刻特定卡片边框、头像位置等，需要 upstream 后续支持或做扩展，不能只新增一个 theme JSON 就解决。

仓库当前没有发现自动化测试目录；核心 `format.py` 体积较大，因此暂时把它定位为**可选高级 formatter**，而不是取代苍何成为全局唯一排版引擎。

### License 边界

README 明确写 `MIT`，但当前 GitHub 仓库元数据 `license=null`，根目录列表也没有独立 `LICENSE` 文件。

因此在许可证文本明确前：

- 可以把它作为外部 upstream 让用户自行安装和调用；
- 本仓库不 vendor、不复制其 `SKILL.md`、脚本、主题或模板；
- 不基于其代码做本地长期 fork。

当前 README 安装方式：

```bash
cd ~/.claude/skills/
git clone https://github.com/xiaohuailabs/xiaohu-wechat-format.git
cp xiaohu-wechat-format/config.example.json xiaohu-wechat-format/config.json
pip3 install markdown requests
```

纯排版不需要微信公众号 AppID/AppSecret。

### 在本项目中的职责边界

只使用它的**排版能力**：

```text
article.md
→ xiaohu-wechat-format / scripts/format.py
→ 微信兼容 HTML
→ canghe-post-to-wechat
```

不使用它自己的：

```text
cover/generate.py
scripts/publish.py
```

原因是封面/配图与发布已经有苍何链路，避免同时维护两套上传和草稿箱逻辑。

## 5. 不作为默认主链：wechat-article-writer

来源：`xstongxue/best-skills`。

它提供通用公众号写作、配图和上传，但与苍何生产链存在明显职责重叠，而且默认研究逻辑更偏通用自媒体 / 技术内容。

因此当前架构不把它作为必需依赖。若用户未来明确指定使用，可单独评估，而不是同时维护两套发布链。

## 6. 排版路由

```text
普通学术长文 / 常规公众号正文
→ canghe-markdown-to-html

专家访谈 / Q&A / 对话 / 卡片 / timeline / hero 等组件化布局
→ xiaohu-wechat-format

最终发布
→ canghe-post-to-wechat
```

如果用户明确要求头像型访谈卡，而当前 xiaohu upstream 仍不支持头像，不要假装已经完成 1:1 复刻；明确说明能力缺口，再决定是否等待 upstream、请求上游增强或在许可证边界明确后另做扩展。

## 7. 总体编排原则

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
可选 canghe-article-illustrator
        ↓
排版路由：canghe 常规 / xiaohu 高级组件
        ↓
canghe-post-to-wechat
```

原则不是“所有 upstream 都不能复制”，而是：优先直接依赖；只有在**实际安装不可达且许可证允许**时，才保留一个明确标注来源、固定版本、许可证完整、尽量不修改且受完整性锁保护的 vendored 副本。当前只对 `content-research-writer` 使用这一例外。
