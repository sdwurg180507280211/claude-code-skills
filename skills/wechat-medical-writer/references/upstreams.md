# Upstreams

本 Skill 不重写成熟 Writer、排版或公众号发布实现，而是把它们作为 upstream 使用。只有 upstream 明确缺少、且本项目确实需要的**小型品牌视觉差异**，才允许在本 Skill 中做独立后处理器。

## 1. 主 Writer：content-research-writer

来源：`CommandCodeAI/agent-skills`

上游路径：`skills/content-research-writer/SKILL.md`

已审计版本：`f490dd9016f2729311e90f317dcb6c98be1a1500`

职责：主题理解、研究、资料整理、大纲、引用、Hook、正文、分节反馈、最终润色与用户风格保持。

这是默认且必需的“主题 → 高质量文章”上游。`wechat-medical-writer` 只向它补充医学领域上下文和 `medical-constraints.md`，不改写它的写作流程。

### Handoff

开始大纲、研究或正文前，把已知的主题、受众、目标、篇幅/形式、用户资料、参考样稿、风格要求、医学上下文和医学约束一次性交给 `content-research-writer`。用户要求“一口气成稿”时，可以连续执行其原生步骤，不要求每个协作节点停下来确认。

如果运行时无法调用主 Writer，停止正文创作并报告依赖问题；不要让医学 Skill 自己承担隐形 fallback Writer。

### 本仓库安装方式

由于该 upstream 在用户可用插件市场中不可达，本仓库按 MIT License 将已审计版本受控 vendor 到：

```text
skills/content-research-writer/
├── SKILL.md
├── LICENSE
├── UPSTREAM.md
└── UPSTREAM.lock.json
```

并加入 `utility-skills` bundle。这个副本不加入医学特有逻辑，并由完整性锁防止无意魔改。

## 2. 可选传播润色：Viral Writer

来源：`nashsu/Viral_Writer_Skill`

已审计版本：`1c76f891fb928ceb22fd101044d100d759f8cee5`

用途仅限标题、开头吸引力、段落节奏、可读性和公众号传播表达。不得让它生产或修改医学事实、数字、引用、指南或监管结论。

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

职责：正文配图（按需）、常规 Markdown → 微信 HTML、发布前处理、上传公众号草稿箱。

纯研究/写作任务不依赖苍何。需要时安装：

```text
/plugin marketplace add freestylefly/canghe-skills
/plugin install content-skills@canghe-skills
/plugin install utility-skills@canghe-skills
```

配图继续叠加 `medical-constraints.md`。本仓库不复制苍何代码，也不维护另一套微信发布实现。

## 4. 高级公众号布局：xiaohu-wechat-format

来源：`xiaohuailabs/xiaohu-wechat-format`

已审计版本：`dbddf0fd9c1189a6f3e0bec1bebb1b0e47e8ddf0`

已审计能力：

- Markdown → 微信兼容 inline HTML；
- `:::dialogue[标题]` 左右对话气泡；
- `:::intro`；
- gallery / stat / timeline / steps / compare / quote / byline / video；
- `interview` 等主题；
- 主题画廊、CJK 排版、中文标点、外链脚注。

适合专家访谈、Q&A、圆桌、导语卡和其他普通 Markdown 难以表达的公众号布局。

### 当前限制

已审计 `:::dialogue` 只支持：

```text
说话人文本 + 内容 + 左右交替气泡
```

没有头像/Logo字段；而且部分 dialogue/intro 样式写在 `scripts/format.py`，并非全部由主题 JSON 控制。

### License 边界

README 声明 MIT，但当前 GitHub metadata `license=null` 且根目录没有独立 `LICENSE` 文件。因此：

- 只让用户外部安装和调用；
- 本仓库不 vendor、不复制它的 `SKILL.md`、脚本、主题或模板；
- 不基于它做长期 fork。

当前安装方式：

```bash
cd ~/.claude/skills/
git clone https://github.com/xiaohuailabs/xiaohu-wechat-format.git
cp xiaohu-wechat-format/config.example.json xiaohu-wechat-format/config.json
pip3 install markdown requests
```

本项目只使用 xiaohu 的 formatter，不使用它的 `cover/generate.py` 或 `scripts/publish.py`。最终发布仍优先 `canghe-post-to-wechat`。

## 5. 本地品牌适配器：Guangyu avatar dialogue

这**不是 upstream**，而是为了补 xiaohu 一个已经明确验证的窄缺口而维护的小型后处理器：

```text
skills/wechat-medical-writer/scripts/enhance_guangyu_dialogue.py
```

输入契约：

```text
xiaohu 已格式化 HTML（依赖 data-container 标记）
+ 运行时 speaker → avatar/logo JSON
```

输出：

```text
同一正文内容
+ 光愈在线式红色完整描边 intro
+ 左右头像/Logo
+ 50px 品牌红头像环
+ #F2F2F2 对话卡
+ 自行实现的 CSS 三角尾巴
```

它不复制 xiaohu 源码，不复制用户样本 HTML/SVG，不解析 Markdown，不生成内容/图片，不发布微信。speaker 缺映射时失败而不是静默降级。确定性行为由 `tests/test_guangyu_dialogue.py` 离线验证。

这类本地适配器允许存在的原因是：它只补**品牌视觉差异**，而不是重新实现 Markdown → HTML formatter。如果以后 xiaohu 原生支持等价头像组件，应优先删除/简化本适配器，而不是继续分叉。

## 6. 不作为默认主链：wechat-article-writer

来源：`xstongxue/best-skills`。

它提供通用公众号写作、配图和上传，但与苍何生产链明显重叠，默认研究逻辑也更偏通用自媒体/技术内容，因此不作为必需依赖。

## 7. 排版与发布路由

```text
普通学术长文 / 常规公众号正文
→ canghe-markdown-to-html

专家访谈 / Q&A / 卡片 / timeline / hero
→ xiaohu-wechat-format

光愈在线式头像访谈
→ xiaohu-wechat-format
→ enhance_guangyu_dialogue.py

最终发布
→ canghe-post-to-wechat
```

## 8. 总体编排原则

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
排版路由：canghe 常规 / xiaohu 高级 / Guangyu 窄后处理
        ↓
canghe-post-to-wechat
```

原则不是“所有 upstream 都不能复制”，而是优先直接依赖。只有在实际安装不可达、许可证允许且当前链路必需时，才保留受控 vendored 副本；当前仅 `content-research-writer` 属于此例外。品牌后处理器则必须保持小型、确定性、可测试，并在 upstream 获得等价能力时优先收缩。
