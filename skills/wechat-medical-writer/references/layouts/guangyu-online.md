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

这说明应把它理解成一套**品牌组件库**，而不是一个固定文章模板。

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
body                 15px / 1.8 / 0.5px letter-spacing
```

用途：文章背景、问题提出、访谈嘉宾/研究背景简介。

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

头像下方还有一个红色对话尾巴，样本通过 inline SVG 实现。

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

这部分正是当前 `xiaohu-wechat-format :::dialogue` 与目标样式的主要差距：xiaohu 有左右气泡，但当前审计版本没有头像/Logo字段。

### 3.7 Summary `summary-chip`

样本中的 Summary 不是普通 H2，而是一个轻量标签：

```text
label text           #F24D60
label background     rgba(249,204,219,0.46)
padding              3px 5px
```

旁边配细线，再接总结段落。不要把 `Summary` 强制加入每篇文章；只有文章结构需要总结卡时使用。

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

常见组件：

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

常见组件：

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

常见组件：

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

## 5. 与现有 upstream 的映射

### 可以直接映射

| 目标组件 | xiaohu-wechat-format | 苍何 |
|---|---|---|
| 常规 Markdown 正文 | 支持 | 支持 |
| 微信 inline HTML | 支持 | 支持 |
| 左右对话气泡 | `:::dialogue` | 非主要强项 |
| 导语块 | `:::intro` | 可通过主题正文实现 |
| timeline / steps / compare | 原生容器 | 视主题能力 |
| 常规学术长文 | 可用 `academic-paper` 等 | **默认优先** |
| 专家访谈结构 | **优先 xiaohu `interview` + `:::dialogue`** | 发布仍用苍何 |
| 正文配图 | 不作为本项目默认生成器 | **canghe-article-illustrator** |
| 草稿箱发布 | 本项目不用 xiaohu publish | **canghe-post-to-wechat** |

### 当前不能 1:1 映射

以下目标效果在已审计 `xiaohu-wechat-format` 中没有直接字段：

```text
对话头像/品牌 Logo
50px 品牌红头像环
头像下 SVG 对话尾巴
光愈在线专属顶部 HOT/关注条
完整的 Summary 标签 + 线条组合
样本专属 END 横线/品牌小图
```

因此当前状态应描述为：

```text
内容结构：可复现
微信兼容 HTML：可复现
通用访谈视觉：可复现
“光愈在线式”品牌细节：需要小型扩展
```

不要把结构近似说成视觉 1:1。

## 6. 当前推荐路由

```text
普通医学长文
→ canghe-markdown-to-html

用户明确要求“光愈在线式学术排版”
→ 读取本 layout profile
→ 优先 xiaohu 高级 formatter / 合适主题
→ 对不能原生表达的品牌组件明确能力缺口

专家访谈 / Q&A
→ article.md 中使用 :::intro / :::dialogue 等结构标记
→ xiaohu interview 主题
→ 当前先生成无头像结构版
→ 若要求 1:1 头像卡：进入“品牌组件扩展”任务，不静默降级

发布
→ canghe-post-to-wechat
```

## 7. 后续扩展边界

如果要做到用户提供截图的高还原版本，最小新增能力只应补**品牌组件**，不重写 Markdown/微信 HTML 引擎：

```text
brand-follow
avatar-dialogue
summary-chip
end-divider
```

优先顺序：

1. 先确认 upstream 是否新增头像/自定义容器能力；
2. 若仍缺失，再做独立的小型后处理/组件层；
3. 该组件层只接收已完成内容和真实头像/Logo素材，不负责医学写作、事实生产、配图生成或微信发布；
4. 不复制用户提供的原始 HTML、图片或第三方编辑器代码到公共仓库。
