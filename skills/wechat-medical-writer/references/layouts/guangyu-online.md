# 光愈在线公众号布局画像

> 用途：这是**视觉/排版参考画像**，不是医学知识库、文章模板或事实来源。
>
> 来源：用户在运行时提供的 `光愈在线公众号.zip`，包含 11 篇已保存微信公众号 HTML 及本地资源。原始 HTML、图片、视频和 ZIP **不提交本仓库**。本文件只记录跨文章重复出现的结构、尺寸、颜色和 upstream 映射。

## 1. 样本结论

对 11 篇文章的 `#js_content` 与 inline style 做结构检查后，可以确认这套公众号不是“整篇长图”，而是：

```text
微信公众号富文本 HTML
+ 局部图片
+ 微信原生视频/小程序组件
+ 大量 <section style="..."> 组件化布局
```

样本中稳定出现的品牌/收尾元素：

| 组件 | 样本出现数（11篇） |
|---|---:|
| `HOT / 点击蓝字 关注我们` 顶部关注条 | 11 |
| 红色描边导语卡 | 8 |
| `END` 收尾 | 10 |
| 免责声明 | 11 |
| 责任编辑 | 10 |
| 审批编号 | 8 |
| 小程序入口 | 8 |
| Reference / 参考文献 | 5 |
| 专家访谈灰色左右气泡 | 2 |
| 专家点评 | 2 |
| Summary 标签 | 2 |

因此应该把“光愈在线风格”理解成一套**品牌组件库**，而不是一个固定写作模板。

## 2. 品牌视觉 Token

从样本 inline style 中抽取的高频视觉值：

```text
brand_accent          #F24D60   rgb(242,77,96)
brand_red             #FF4545   rgb(255,69,69)
soft_pink             #FFEEEA   rgb(255,238,234)
dialogue_bg           #F2F2F2   rgb(242,242,242)
intro_outer_bg        #FFFFFF
follow_outer_bg       #F1F8FD   rgb(241,248,253)
body_text             #3E3E3E   rgb(62,62,62)
heading_brown         #5F401C   rgb(95,64,28)
secondary_gray        #6F6E6E   rgb(111,110,110)
```

常见正文参数：

```text
正文                 15px 左右
正文 line-height      1.8 左右
导语正文             15px / line-height 1.8 / letter-spacing 0.5px
访谈问题/回答         15px / line-height 1.8
```

这些 Token 只用于复现用户指定的视觉方向；不要把它们反向解释成文章内容结构规则。

## 3. 核心组件画像

### 3.1 顶部关注条 `brand-follow`

11/11 样本出现。

视觉组成：

```text
浅蓝灰圆角底
├─ 红色 HOT 小胶囊
├─ 细线/装饰
└─ “点击蓝字 关注我们”
```

观察到的关键值：

```text
outer background   #F1F8FD
outer radius       20px
HOT background     #F24D60
HOT radius         12px
HOT font           9px / white
label font          14px 左右
```

这属于品牌 chrome，不应该由主 Writer 生成医学内容时硬编码。

### 3.2 导语卡 `intro-card`

8/11 样本出现，是最稳定的正文开场组件之一。

在访谈样本中实际值接近：

```text
background          #FFFFFF
border              2px solid #F24D60
border-radius       10px
padding             22px 23px
margin              20px 0 10px
body                15px / 1.8 / 0.5px letter-spacing
```

用途：文章背景、问题提出、访谈嘉宾/研究背景简介。

**当前实现：** `scripts/enhance_guangyu_dialogue.py` 会在 xiaohu 已生成的 HTML 上，把 `data-container="intro"` 改成这一完整红色描边视觉。它不生成导语内容。

### 3.3 章节标题 `section-heading`

学术/文献解读类文章常见两种骨架，不能强制所有文章使用同一种。

**A. 研究型大章节：**

```text
大号编号（如 01）    24px / #5F401C
标题底               #FFEEEA
标题容器 padding     10px 20px
```

常用于：研究背景、研究设计、研究结果、研究结论。

**B. 条目型小编号：**

```text
01 / 02 / 03
编号下方约 5px soft-pink 底线
正文标题 + 解释内容
```

常用于分类、临床启示、机制要点、结果拆解。

### 3.4 专家点评 `expert-comment`

在文献/研究解读文章中出现。

标签视觉：

```text
background          #F24D60
text                white
left border         12px solid #FFEEEA
padding             4px 12px
```

后接专家点评正文。这个组件是“内容类型标签”，不是证据等级标记；其中事实仍受医学核验规则约束。

### 3.5 左侧提问 `interview-question`

真实样本结构：

```text
[品牌 Logo 圆形头像]  [灰色问题卡]
```

关键参数：

```text
row                  display:flex; justify-content:flex-start
avatar column        60px
avatar ring          50x50px
avatar ring bg       #F24D60
avatar padding       4px
inner image          40px 左右，白色圆边
bubble bg            #F2F2F2
bubble radius        5px
bubble padding       10px 20px
bubble margin        20px 15px 0 -30px
text                 #000 / 15px / 1.8
```

原始样本头像下方使用 inline SVG 对话尾巴。

**当前实现：** xiaohu 先生成 `data-container="dialogue-bubble" data-side="left"`；随后 `enhance_guangyu_dialogue.py` 根据 speaker→image 映射注入 60px 头像列、50px 品牌红头像环、灰色气泡和自行实现的 CSS 三角尾巴。脚本不复制样本 SVG。

### 3.6 右侧回答 `interview-answer`

真实样本结构：

```text
[灰色专家回答卡]  [专家圆形头像]
```

关键参数：

```text
row                  display:flex; justify-content:flex-end
avatar column        60px
avatar ring          50x50px
avatar ring bg       #F24D60
bubble bg            #F2F2F2
bubble radius        5px
bubble padding       15px 20px
bubble margin        20px -30px 0 15px
text                 #000 / 15px / 1.8
```

**当前实现：** 与左侧提问使用同一品牌适配器，只是头像在右、气泡在左。speaker 必须在运行时头像映射中存在；缺失时脚本失败并报告，不静默输出半成品。

### 3.7 Summary `summary-chip`

样本中的 Summary 不是普通 H2，而是一个轻量标签：

```text
label text           #F24D60
label background     rgba(249,204,219,0.46)
padding              3px 5px
```

旁边配细线，再接总结段落。不要把 `Summary` 强制加入每篇文章；只有文章结构需要总结卡时使用。

**当前状态：** 尚未做专属品牌适配器。可先由 xiaohu 普通 callout/标题近似；若用户要求高还原，再单独增加 `summary-chip`，不要扩张 `avatar-dialogue` 的职责。

### 3.8 专家资料 `expert-profile`

访谈文章可能在正文后加入专家简介：

```text
“解读专家”装饰标题
专家照片
姓名/职称
学术任职条目
```

样本中姓名小标签使用 `#F24D60` 背景、浅色文字。是否出现由当前文章是否需要嘉宾介绍决定。

### 3.9 `END` 收尾

高频固定视觉：

```text
2px 红色横线
中间/上层白底 END 标签
END color            #FF4545
```

样本还常在横线旁放约 65px 品牌装饰图片。

**当前状态：** 尚未做专属品牌适配器。不要为了一个 END 组件复制样本图片；需要时由用户提供真实品牌资产，再增加独立 `end-divider`。

### 3.10 合规尾注

样本常见顺序：

```text
END
→ Reference / 参考文献（如有）
→ 审批编号（如有）
→ 免责声明
→ 撰稿/责任编辑（按文章情况）
```

这些字段的“是否存在/具体文本”必须来自用户当次要求或真实业务数据，不能因为样本有就自动编造审批编号、责任编辑或声明内容。

## 4. 文章类型，而不是固定模板

11 篇样本可归纳成四类视觉用法：

### A. HCP 学术长文 / 共识解读

```text
brand-follow
intro-card
section-heading
numbered-point / data figure
Reference
END
compliance footer
```

适合：HPV 分型、指南/共识、HSIL/CIN 风险管理。

### B. 文献 / 临床研究解读

```text
brand-follow
intro-card
研究背景 / 研究设计 / 研究结果 / 研究结论
figure / table
expert-comment（可选）
Reference
END
compliance footer
```

### C. 专家访谈 / Q&A

```text
brand-follow
intro-card
video（可选）
interview-question
interview-answer
...重复若干轮
summary-chip（可选）
expert-profile（可选）
END
compliance footer
```

### D. 品牌/活动信息

可大量使用图片、卡片、小程序，不应强行套学术长文结构。

**重要：** 分类只决定排版组件选择，不决定 Writer 的论证结构。文章结构仍交给 `content-research-writer` 和用户当前需求。

## 5. 与现有 upstream / 本地适配器的映射

| 目标组件 | xiaohu-wechat-format | 本地 Guangyu adapter | 苍何 |
|---|---|---|---|
| 常规 Markdown 正文 | 支持 | 不处理 | 支持 |
| 微信 inline HTML | 支持 | 只后处理已有 HTML | 支持 |
| 左右对话气泡 | `:::dialogue` | 加头像/品牌视觉 | 非主要强项 |
| 导语块 | `:::intro` | 改成红色完整描边卡 | 可通过主题正文实现 |
| timeline / steps / compare | 原生容器 | 不处理 | 视主题能力 |
| 常规学术长文 | 可用 `academic-paper` 等 | 不处理 | **默认优先** |
| 专家访谈结构 | **interview + :::dialogue** | **高还原头像卡** | 发布仍用苍何 |
| 正文配图 | 不作为本项目默认生成器 | 不生成图片 | **canghe-article-illustrator** |
| 草稿箱发布 | 本项目不用 xiaohu publish | 不发布 | **canghe-post-to-wechat** |

当前已经补齐：

```text
intro-card
avatar-dialogue（左右头像/Logo + 品牌红头像环 + 灰色气泡 + CSS 尾巴）
```

仍未做专属高还原：

```text
brand-follow（HOT/关注条）
summary-chip + 线条组合
end-divider + 品牌装饰图
expert-profile 专属皮肤
```

因此当前状态应描述为：

```text
内容结构：可复现
微信兼容 HTML：可复现
访谈左右头像卡：已有本地小型适配器
完整“光愈在线式”全篇品牌细节：尚未全部 1:1
```

## 6. 头像访谈适配器

文件：

```text
scripts/enhance_guangyu_dialogue.py
```

职责很窄：

```text
xiaohu 已生成 HTML
+ speaker → avatar/logo JSON
→ Guangyu-style intro + avatar dialogue HTML
```

输入映射示例：

```json
{
  "光愈在线": "assets/logo.png",
  "梁静教授": "assets/liang.png"
}
```

调用：

```bash
python3 scripts/enhance_guangyu_dialogue.py \
  --input /path/to/formatted.html \
  --avatars /path/to/avatars.json \
  --output /path/to/formatted.guangyu.html
```

行为约束：

- 只读取 xiaohu 的 `data-container` 标记，不解析 Markdown；
- 不依赖 xiaohu Python 源码，不复制其主题；
- 不读取用户原始公众号样本；
- 不下载/生成头像；
- speaker 缺头像映射时失败并明确列出缺失项；
- 头像路径可以是后续发布链可解析的本地路径或 URL；
- `--accent` 可覆盖品牌色，默认 `#F24D60`；
- 使用 Python 标准库，无新增 runtime dependency。

测试：`tests/test_guangyu_dialogue.py` 使用合成的 xiaohu-like HTML，不包含用户私有素材。

## 7. 当前推荐路由

```text
普通医学长文
→ canghe-markdown-to-html

光愈在线式学术长文（非访谈）
→ 读取本 layout profile
→ 选择 canghe / xiaohu 合适主题
→ 不强制调用头像适配器

专家访谈 / Q&A（普通）
→ article.md 使用 :::intro / :::dialogue
→ xiaohu interview 主题

光愈在线式头像访谈
→ article.md 使用 :::intro / :::dialogue
→ xiaohu interview 主题
→ enhance_guangyu_dialogue.py + 用户真实头像/Logo映射
→ canghe-post-to-wechat
```

## 8. 后续扩展边界

如果继续提高还原度，只补还缺的**品牌组件**，不重写 Markdown/微信 HTML 引擎：

```text
brand-follow
summary-chip
end-divider
```

原则：

1. 先确认 upstream 是否新增等价能力；
2. 缺失时再做独立、可测试的小型后处理组件；
3. 每个组件只接收已完成内容和真实品牌素材，不负责医学写作、事实生产、配图生成或微信发布；
4. 不复制用户提供的原始 HTML、图片、SVG 或第三方编辑器代码到公共仓库；
5. 不因为样本 11/11 出现某组件，就强制所有未来文章必须出现它。
