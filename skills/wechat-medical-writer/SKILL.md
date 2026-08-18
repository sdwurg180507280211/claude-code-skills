---
name: wechat-medical-writer
description: 医学类微信公众号/服务号的轻量编排 Skill。它只提供医学领域上下文、必要医学事实约束和 upstream handoff，不自定义文章结构、标题方法、研究流程、模板、Claim Ledger 或发布实现。主题到高质量文章必须交给本仓库随 utility-skills 一起提供的 content-research-writer；配图、Markdown 转微信 HTML、上传草稿箱按需交给苍何 canghe-article-illustrator / canghe-markdown-to-html / canghe-post-to-wechat。当前领域方向为女性健康、妇科、宫颈疾病、HPV、HSIL、CIN2/CIN3、生育力保护、PDT/HAL-PDT 等。用户上传的医学 ZIP/PPT 只用于定义领域方向或作为当次参考资料，原件不提交仓库。
---

# Medical WeChat Writer

## 定位

这是一个**医学领域适配与编排层**，不是新的通用写作引擎。

它只负责：

1. 告诉上游 Writer 当前服务号长期关注哪些医学领域；
2. 把用户本次提供的医学资料、参考文章和约束传给上游 Writer；
3. 增加少量医学事实边界，避免把营销材料、样稿或模型常识当成医学证据；
4. 在需要配图、排版或上传时，把成稿继续交给已经存在的苍何 Skill。

它**不负责重新发明**：选题方法、Hook、标题方法、大纲方法、文章节奏、固定文章模板、研究工作流、公众号排版、配图实现或微信发布代码。

## 当前医学方向

当前领域方向来自用户提供的私有医学资料包，但资料包只定义“以后主要写什么”，不定义“文章必须怎么写”。

领域概览：

```text
女性健康
└── 妇科 / 宫颈健康
    ├── HPV 感染与持续感染
    ├── 宫颈癌筛查与防治
    ├── LSIL / HSIL
    ├── CIN2 / CIN3
    ├── 阴道镜 / 病理 / 风险分层
    ├── 生育需求与宫颈功能保护
    ├── 观察与治疗选择
    └── PDT / HAL-PDT
```

更完整的范围见 `references/domains/cervical-health.md`。

注意：这个领域文件只是 taxonomy，不是医学知识库，也不是文章模板。

## 上游优先

### 主题 → 研究 → 高质量文章

必须使用：

```text
content-research-writer
```

它负责其原生的研究、资料整理、大纲、引用、Hook、正文创作、迭代和最终润色流程。本 Skill 不复制或重写这些能力。

由于该 upstream 目前不在用户可用的插件市场中，本仓库已经按 MIT License 将其 vendored 为独立 `skills/content-research-writer/`，并加入 `utility-skills` bundle。安装 `utility-skills@my-skills` 后，应直接使用这个本地 Skill，不再因为“市场里没有 upstream”而启用自制 fallback Writer。

如果用户只手动安装了 `wechat-medical-writer` 而没有安装 `content-research-writer`，应明确提示补装同仓库的 `content-research-writer`，不要自己重写一套 Writer。

### 强制 Handoff Contract

**在开始大纲、研究或正文之前，先把通用写作阶段交给 `content-research-writer`。** 不允许先由本 Skill 自己写一篇，再把 upstream 当作可选润色器。

向主 Writer 传递当前已经知道的上下文，至少包括可获得的：

```text
topic              当前主题 / 核心问题
audience           医生 / HCP / 患者 / 公众 / 其他
goal               教育 / 解读 / 综述 / 证据分析等
format_length      用户指定的形式与篇幅（如有）
user_sources       当前附件、私有资料或指定来源
reference_sample   用户给的优秀公众号样稿（如有）
style_constraints  用户指定的语气、完成度、引用方式（如有）
medical_context    references/domains/cervical-health.md
medical_constraints references/medical-constraints.md
```

规则：

- 上下文里已经明确的信息不要重复询问用户；
- 真正影响准确性、受众或任务目标的必要信息缺失时，再按主 Writer 原生流程询问；
- 用户明确说“直接写一篇 / 一口气完成 / 给我成稿”时，仍使用主 Writer 的原生步骤，但可在同一轮连续完成大纲 → 研究 → 草稿 → 引用检查 → 最终润色，不必人为停在每个协作节点等待确认；
- 如果运行环境实际上无法调用或加载 `content-research-writer`，停止正文创作并报告缺少依赖；**不得改成模型自行执行一个隐形 fallback Writer**。

### 可选表达优化

`Viral Writer` 只可在用户明确要求更强的公众号传播表达、标题或节奏时作为**可选润色层**。它不得新增、删除或改写医学事实、数字、指南结论、适应证、监管状态和参考文献。

## 医学约束

只叠加上游通用 Writer 不具备的医学边界，见 `references/medical-constraints.md`。

核心要求：

- 不虚构指南、共识、论文、作者、年份、DOI/PMID、样本量、统计结果或监管状态；
- 不把课件、营销材料或参考文章中的推广语直接升级成医学事实；
- 面向公开发布的医学文章，即使用户没有额外说“核验”，关键医学数字、指南推荐、疗效/安全性、适应证和监管结论也应有可追溯来源；
- 用户明确要求“只基于我提供的资料、不做外部核验”时可以遵从，但最终稿要明确标识这一来源边界；
- 成稿前检查正文引用与参考文献一一对应，具体数字能够回到实际来源；
- 如果当前来源不足以支持某个医学结论，明确说明不足，不替用户补一个确定答案；
- 不强制生成 Claim Ledger、source map、固定审核表或额外工作目录，除非用户明确要求。

## 处理用户资料

### 医学 ZIP / PPT / PDF

用户提供的医学资料可能有两种作用：

- **领域方向**：告诉系统长期关注哪些疾病、诊疗场景和专业主题；
- **当次来源**：用户明确要求基于这些资料写文章时，把资料交给上游 Writer 使用。

不要因为资料曾经被用于定义领域，就默认以后每篇文章只能来自这些资料。

不要把原始 ZIP/PPT/PDF、内部培训材料、未公开资料或患者资料提交到本 GitHub 仓库。

### 参考公众号文章

如果用户提供一篇优秀文章作为样稿：

- 可以把它作为结构、语气、信息密度、标题层级、引用呈现方式和整体完成度的参考；
- 不把样稿里的医学结论、数字或参考文献自动视为已核验来源；
- 不把样稿的固定结构硬编码成以后所有文章的模板；
- 上游 Writer 应根据当前主题和用户要求决定最终文章结构。

例如用户提供一篇“HCP 学术型服务号文章”，目标是达到类似的专业程度和完成度，而不是逐段套模板。

## 配图 / 排版 / 草稿箱

这些步骤是**按需下游**，不要阻塞纯写作任务。

### Preflight

如果用户只要求研究或写文章，不要求安装苍何。

只有当用户要求“配图 / 排版 / 转微信 HTML / 上传草稿箱 / 发布”时，才检查以下 Skill 是否可用：

```text
canghe-article-illustrator
canghe-markdown-to-html
canghe-post-to-wechat
```

若缺少苍何 upstream，明确给出安装方式，不自行实现替代版本：

```text
/plugin marketplace add freestylefly/canghe-skills
/plugin install content-skills@canghe-skills
/plugin install utility-skills@canghe-skills
```

安装完成后按需求调用：

```text
canghe-article-illustrator     # 可选：正文配图
canghe-markdown-to-html        # 微信公众号 HTML 排版
canghe-post-to-wechat          # 上传公众号草稿箱
```

医学配图必须继续遵守 `references/medical-constraints.md`：数据图只使用已核验数据并保留来源；机制图不得把推测画成已证实因果；产品/器械优先使用用户提供的官方素材，不让生成模型虚构官方产品资产。

这些能力由苍何 upstream 负责，本仓库不复制实现。详细 upstream 说明见 `references/upstreams.md`。

## 推荐编排

```text
用户主题 / 用户资料 / 参考文章
        ↓
wechat-medical-writer
只补充领域上下文 + 医学约束
        ↓
【MANDATORY】content-research-writer
使用其原生写作流程完成研究与成稿
        ↓
引用完整性 / 医学事实边界检查
        ↓
（可选）Viral Writer
只做表达/标题/节奏润色，不改变医学事实
        ↓
（用户需要时）苍何 preflight
        ↓
（可选）canghe-article-illustrator
        ↓
canghe-markdown-to-html
        ↓
canghe-post-to-wechat
        ↓
微信公众号草稿箱
```

## 输出

本 Skill 不规定固定输出文件集合。

默认以**上游 Writer 的原生输出**为准。通常是一篇可继续处理的 Markdown 文章；是否同时输出研究笔记、引用列表、标题方案、配图建议等，由上游 Skill 和用户当前要求决定。

## 仓库边界

`wechat-medical-writer` 自身只保存：

```text
SKILL.md
references/domains/cervical-health.md
references/medical-constraints.md
references/upstreams.md
README.md
```

用户原始医学资料不进入仓库。唯一的 Writer 提示词副本是独立目录 `skills/content-research-writer/`，它是为解决安装可用性而保留的、带 MIT License、upstream provenance 和完整性锁的 vendored 副本，不在医学 Skill 内进行二次改写。
