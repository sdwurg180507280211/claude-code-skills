---
name: wechat-medical-writer
description: 医学类微信公众号/服务号的领域上下文与参考资料适配层。当前重点是女性健康、妇科、宫颈疾病、HPV、HSIL、CIN2/CIN3、生育力保护、PDT/HAL-PDT。用户提供的 ZIP/PPT/PDF 等材料作为医学参考资料使用，但本 Skill 不自行规定文章结构、写作方法、标题策略、配图流程或发布流程；这些能力直接复用现成写作与微信公众号 Skill。
---

# Medical WeChat Writer Context

## 定位

本 Skill **不是新的文章写作引擎**。

它只负责两件事：

1. 为医学类微信公众号/服务号提供当前领域上下文。
2. 把用户提供的医学 ZIP / PPT / PDF / Word / 论文 / 指南等作为写作任务的参考资料交给现成写作 Skill 使用。

文章如何构思、如何编排、如何拟标题、如何写正文、如何生成配图、如何排版和发布，均由用户选择的现成 Skill 按它自己的 `SKILL.md` 执行；本 Skill 不覆盖、不重写、不合并这些成熟流程。

## 当前医学方向

当前参考资料包所覆盖的服务号方向包括：

```text
女性健康
└── 妇科 / 宫颈疾病
    ├── HPV 感染
    ├── 宫颈癌防治
    ├── LSIL / HSIL
    ├── CIN2 / CIN3
    ├── 阴道镜 / 病理
    ├── 风险分层与随访
    ├── 生育需求 / 生育力保护
    ├── 宫颈病变治疗
    └── PDT / HAL-PDT
        ├── 作用机制
        ├── 临床研究
        ├── 指南 / 共识
        ├── 疗效与安全性
        ├── 治疗流程
        └── 产品医学教育
```

更详细的领域索引见 `references/domains/cervical-health.md`。

## 用户资料的角色

用户当前提供的医学压缩包及其中课件是**参考资料**，不是写作模板，也不是唯一信息源。

使用原则：

- 当任务要求“根据上传资料写”时，以资料实际支持的内容为依据。
- 不因为领域索引里出现某个主题，就假定压缩包已经支持某个具体结论。
- 如果用户要求查最新指南、论文、监管信息或补充外部证据，由所选上游写作/研究 Skill 按其既有流程完成。
- 用户资料与外部资料可以同时用于文章，但不要把外部新增内容伪装成来自上传课件。
- 原始 ZIP/PPT/PDF 等文件不提交本 GitHub 仓库。

## 直接复用现成 Skill

不要在本 Skill 中重新实现已有的写作、配图、排版或发布方法。

可复用的现成上游见 `references/upstreams.md`，当前包括：

- `wechat-article-writer`：公众号文章从主题/资料到成稿、标题、配图等完整创作流程。
- `Viral Writer`：从主题或素材生成微信公众号等自媒体完整内容。
- `content-research-writer`：研究型文章的资料检索、outline、引用、撰写与润色。
- `canghe-article-illustrator`：文章配图。
- `canghe-markdown-to-html`：Markdown → 公众号 HTML 排版。
- `canghe-post-to-wechat`：微信公众号草稿箱/发布流程。

### 路由原则

1. 用户明确指定某个写作 Skill：直接使用那个 Skill，本 Skill 只补充医学领域与参考资料上下文。
2. 环境中已有明确匹配的写作 Skill：读取并遵循它自己的 `SKILL.md`，不要把本 Skill 的流程替换进去。
3. 同时存在多个同等适用的写作 Skill 且用户没有指定：不要擅自拼接它们的工作流；让用户选择，或交给宿主已有的 Skill 路由机制。
4. 用户要求排版、配图或发布时，优先直接使用对应的现成苍何 Skill，而不是在这里重写实现。

## 明确不做的事

本 Skill 不再自定义：

- 固定文章大纲
- 医生端/患者端文章模板
- 标题或 Hook 方法论
- 自定义 Claim Ledger
- `source-only` / `source-first` / `research-update` 等私有模式
- 自定义输出目录/文件契约
- 自己的公众号发布脚本
- 自己的 Markdown 排版器
- 自己的配图工作流

除非用户明确要求新增这些规则，否则应保持上游 Skill 的原始行为。

## 私有资料

如果用户直接在当前会话上传资料，直接读取附件即可。

如长期在本地使用，可把原始资料放在仓库外，例如：

```text
~/medical-content-library/
└── cervical-health/
    ├── slides/
    ├── papers/
    ├── guidelines/
    └── notes/
```

这些原始资料不进入 `my-skills` 仓库。
