# 光愈在线公众号布局画像

> 用途：这是**视觉/排版参考画像**，不是医学知识库、文章模板或事实来源。
>
> 来源一：用户运行时提供的 `光愈在线公众号.zip`，包含 11 篇已保存微信公众号 HTML 及本地资源。
>
> 来源二：用户后续提供的已发布文章截图与封面色调反馈，用于补充**视觉偏好**。原始 HTML、截图、图片、视频和 ZIP **不提交本仓库**。

## 1. 样本结论

这套公众号不是“整篇长图”，而是：

```text
微信公众号富文本 HTML
+ 局部图片 / 统计图
+ 微信原生视频 / 小程序组件
+ 大量 <section style="..."> 组件化布局
```

11 篇样本中稳定出现的品牌/收尾元素：

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

因此，“光愈在线风格”应理解为一套**品牌组件与视觉 Token**，而不是固定写作模板。文章结构仍由上游 Writer 和当次内容决定。

---

## 2. 品牌视觉 Token

### 2.1 正文品牌色

从样本 inline style 中抽取的高频值：

```text
brand_accent          #F24D60   rgb(242,77,96)
brand_red             #FF4545   rgb(255,69,69)
soft_pink             #FFEEEA   rgb(255,238,234)
dialogue_bg           #F2F2F2   rgb(242,242,242)
intro_outer_bg        #FFFFFF
follow_outer_bg       #F1F8FD   rgb(241,248,253)
body_text             #3E3E3E   rgb(62,62,62)
heading_text          #333333
heading_brown         #5F401C   rgb(95,64,28)
secondary_gray        #6F6E6E   rgb(111,110,110)
light_border          #F7DDE1
```

### 2.2 用户确认的封面主色调（默认优先）

用户已明确确认：宫颈健康 / HPV 系列封面优先采用**偏沉稳的玫瑰红、豆沙红、暖医学红**，不要默认做成过浅的粉白少女色。

推荐色域：

```text
cover_deep_rose       #B84C5A
cover_mid_rose        #CB626E
cover_warm_red        #D96D78
cover_glow_pink       #F2A1AA
cover_light_pink      #F8D6D9
cover_title           #FFF9F8
cover_secondary       rgba(255,255,255,0.88)
```

视觉方向：

```text
深玫瑰红 → 暖红 → 柔粉的连续渐变
+ 轻暗角 / 中心柔光
+ 半透明医学线框
+ 低对比网络节点 / DNA / 分子纹理
+ 同色系丝带 / 曲面
+ 白色高对比标题
```

要求：

- 2.35:1 公众号封面时，标题必须在缩略图状态仍可读；
- 主标题优先白色或极浅粉白，不在深红底上继续使用深红字；
- 医学元素可使用子宫 / 宫颈、HPV 粒子、保护盾、网络节点，但不要恐怖、写实病理化；
- 封面是主 KV，不做成信息图，不塞正文数字和多层解释；
- 除非用户另行指定，后续同系列封面保持这一色调家族，形成账号识别度。

---

## 3. 正文字体与可读性基线

用户反馈：之前生成的公众号 HTML 相比成熟样稿，**正文文字偏小、标题层级偏弱**。因此光愈在线式长文不再以“15px 能显示”为质量门槛，而采用更适合手机阅读的基线。

### 3.1 正文默认参数

```text
body font-size        16px
body line-height      1.85
body color            #3E3E3E
paragraph margin      0 0 18px
letter-spacing        0 ~ 0.3px
text-align            justify / left（按内容）
```

推荐范围：

```text
普通患者科普正文     16px / 1.85
HCP 学术长文正文     15.5~16px / 1.8~1.85
导语卡正文           15.5~16px / 1.8 / 0.3~0.5px
访谈问答正文         15~16px / 1.8
图注                 12.5~13px / 1.65~1.75 / #737373
References            12~13px / 1.6~1.7 / #6F6E6E
免责声明              12px 左右 / 1.7~1.8 / #888888
```

**不要为了塞更多字把整篇正文压到 14px 或更小。** 公众号在手机端的可读性优先于桌面预览密度。

### 3.2 强调文字

- 正文粗体使用 `font-weight: 600~700`，不要整段全粗；
- 关键结论可用 `#F24D60` 或深色粗体，但不要每段都红；
- 引用 / 核心结论块应通过留白、边线或浅底区分，不依赖超大字号。

---

## 4. 核心组件画像

### 4.1 顶部关注条 `brand-follow`

11/11 样本出现。

```text
outer background     #F1F8FD
outer radius         20px
HOT background       #F24D60
HOT radius           12px
HOT font             9px / white
label font           14px 左右
```

它属于品牌 chrome，不应该由主 Writer 生成医学内容时硬编码。

### 4.2 导语卡 `intro-card`

8/11 样本出现。

```text
background           #FFFFFF
border               2px solid #F24D60
border-radius        10px
padding              22px 23px
margin               20px 0 10px
body                  15.5~16px / 1.8 / 0.3~0.5px letter-spacing
```

用途：文章背景、问题提出、访谈嘉宾/研究背景简介。

`enhance_guangyu_dialogue.py` 会在 xiaohu 已生成 HTML 上，把 `data-container="intro"` 改成完整红色描边视觉；它不生成导语内容。

### 4.3 章节标题 `section-heading-card` —— 高还原优先样式

用户提供的新截图表明，成熟样稿的章节标题不是简单的“01 + 一条粉底”，而是一个有明显品牌层级的**大号白色圆角标题卡**。对于用户明确要求“像光愈在线 / 高还原”时，优先采用这一结构。

视觉结构：

```text
┌──────────────────────────────────────────┐
│   [ 1 ]     高危HPV分型的定义和演变        │
│                                          │
└──────────────────────────────────────────┘
                 红色强调下边线
```

推荐 Token：

```text
outer background     #FFFFFF
outer radius         18~20px
outer border         1px solid #F7DDE1
bottom border        3px solid #F24D60
padding              18~22px 22~28px
margin               28px 0 20px

number box           40~46px square
number radius        10~12px
number gradient      #FF4D65 → #FFB1B9
number text          white / 22~25px / 700
number decorations   两侧轻量 L 形 / 角标线，#F24D60

title                #333333 / 20~22px / 700
title line-height    1.4~1.5
```

原则：

- 标题卡负责建立“章节开始”的视觉重量，不能只靠一个小号 `01`；
- 编号与标题必须在同一水平视觉组中；
- 白底 + 细粉边 + 品牌红下边线，比大面积粉底更高级、更接近用户提供样稿；
- 标题较长时允许两行，不要为了单行缩到 16px；
- 微信最终 HTML 使用 inline style，不依赖外部 `<style>`。

可参考的 HTML 骨架：

```html
<section style="margin:28px 0 20px;padding:20px 24px;background:#fff;border:1px solid #f7dde1;border-bottom:3px solid #f24d60;border-radius:20px;box-sizing:border-box;">
  <section style="display:flex;align-items:center;">
    <span style="display:inline-flex;width:44px;height:44px;align-items:center;justify-content:center;border-radius:11px;background:linear-gradient(135deg,#ff4d65,#ffb1b9);color:#fff;font-size:24px;font-weight:700;margin-right:18px;">1</span>
    <strong style="font-size:21px;line-height:1.45;color:#333;">章节标题</strong>
  </section>
</section>
```

微信编辑器对部分复杂 CSS 的保留可能不同；若渐变被清理，允许退化为 `#F24D60` 实色编号块，但**字号、留白、白色标题卡和红色下边线必须保留**。

### 4.4 章节标题备用样式

只有在文章整体更轻、更简洁或 formatter 不方便输出大标题卡时，才使用旧的研究型 / 条目型标题：

```text
A. 研究型：24px 编号 + #FFEEEA 标题底 + 10px 20px padding
B. 条目型：01 / 02 / 03 + 约 5px soft-pink 底线 + 正文标题
```

用户明确要求高还原时，不应默认回退到这个简化版本。

### 4.5 专家点评 `expert-comment`

```text
background           #F24D60
text                 white
left border          12px solid #FFEEEA
padding              4px 12px
```

它只是内容类型标签，不是证据等级标记。

### 4.6 左侧提问 `interview-question`

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
text                 #000 / 15~16px / 1.8
```

原始样本头像下方使用 inline SVG 对话尾巴；本地 adapter 使用轻量 CSS 尾巴，不复制样本 SVG。

### 4.7 右侧回答 `interview-answer`

```text
row                  display:flex; justify-content:flex-end
avatar column        60px
avatar ring          50x50px
avatar ring bg       #F24D60
bubble bg            #F2F2F2
bubble radius        5px
bubble padding       15px 20px
bubble margin        20px -30px 0 15px
text                 #000 / 15~16px / 1.8
```

speaker 必须在运行时头像映射中存在；缺失时失败并报告，不静默输出半成品。

### 4.8 Summary `summary-chip`

```text
label text           #F24D60
label background     rgba(249,204,219,0.46)
padding              3px 5px
```

旁边配细线，再接总结段落。只有文章结构需要总结卡时使用，不强制每篇出现。

### 4.9 专家资料 `expert-profile`

访谈文章可按需要加入：

```text
“解读专家”装饰标题
专家照片
姓名 / 职称
学术任职条目
```

姓名小标签可使用 `#F24D60` 背景、浅色文字。具体专家资产必须来自用户真实素材。

### 4.10 `END` 收尾

```text
2px 红色横线
中间 / 上层白底 END 标签
END color            #FF4545
```

不要为了一个 END 组件复制样本品牌图片；需要真实品牌装饰时由用户提供。

### 4.11 合规尾注

常见顺序：

```text
END
→ Reference / 参考文献（如有）
→ 审批编号（如有）
→ 免责声明
→ 撰稿 / 责任编辑（按文章情况）
```

审批编号、责任编辑等业务字段不能因为样稿有就自动编造。

---

## 5. 正文统计图 / 论文图风格

用户已确认：医学文章中涉及真实数据时，优先使用**论文式统计图**，而不是卡通科普信息图。

优先视觉：

```text
白底
黑 / 深灰标题与坐标
品牌红数据系列
轻灰网格线
真实数值标签
95% CI（来源有时）
Figure caption
真实来源 / PMID / DOI（经核验）
```

要求：

- 数据图的数值必须来自已核验来源；
- 不让图像生成模型自己发明或改写统计数字；
- 若使用生成模型做视觉重绘，先建立数据锚点，并在正文图注中再次给出核验后的来源；
- 原论文许可不允许直接改图时，基于可合法使用的真实数据独立重绘，不复制原图设计。

---

## 6. 文章类型，而不是固定模板

### A. HCP 学术长文 / 共识解读

```text
brand-follow
intro-card
section-heading-card
numbered-point / data figure
Reference
END
compliance footer
```

### B. 文献 / 临床研究解读

```text
brand-follow
intro-card
section-heading-card
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

### D. 品牌 / 活动信息

可大量使用图片、卡片、小程序，不应强行套学术长文结构。

**分类只决定排版组件选择，不决定 Writer 的论证结构。**

---

## 7. 与 upstream / 本地 adapter 的映射

| 目标组件 | xiaohu-wechat-format | 本地 Guangyu adapter | 苍何 |
|---|---|---|---|
| 常规 Markdown 正文 | 支持 | 不处理 | 支持 |
| 微信 inline HTML | 支持 | 只后处理已有 HTML | 支持 |
| 左右对话气泡 | `:::dialogue` | 加头像 / 品牌视觉 | 非主要强项 |
| 导语块 | `:::intro` | 改成红色完整描边卡 | 可通过主题正文实现 |
| timeline / steps / compare | 原生容器 | 不处理 | 视主题能力 |
| 常规学术长文 | 可用 `academic-paper` 等 | 不处理 | 默认优先 |
| 专家访谈结构 | `interview + :::dialogue` | 高还原头像卡 | 发布仍用苍何 |
| 正文配图 | 不作为默认生成器 | 不生成图片 | canghe-article-illustrator |
| 草稿箱发布 | 本项目不用 xiaohu publish | 不发布 | canghe-post-to-wechat |

当前已补：

```text
intro-card
avatar-dialogue
```

高还原文章排版时，formatter / 生成 HTML 的执行者还应按本文件直接应用：

```text
16px 正文基线
section-heading-card
品牌色 / 留白
论文式统计图图注规范
```

仍未做专属自动 adapter：

```text
brand-follow
section-heading-card 自动后处理
summary-chip + 线条组合
end-divider + 品牌装饰图
expert-profile 专属皮肤
```

因此不要宣称“全篇品牌细节已 1:1 自动化”。

---

## 8. 头像访谈适配器

文件：

```text
scripts/enhance_guangyu_dialogue.py
```

职责：

```text
xiaohu 已生成 HTML
+ speaker → avatar / logo JSON
→ Guangyu-style intro + avatar dialogue HTML
```

输入示例：

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
- 不下载 / 生成真实专家头像；
- speaker 缺头像映射时失败并明确列出缺失项；
- 头像路径可以是后续发布链可解析的本地路径或 URL；
- `--accent` 可覆盖品牌色，默认 `#F24D60`；
- 使用 Python 标准库，无新增 runtime dependency。

测试：`tests/test_guangyu_dialogue.py` 使用合成的 xiaohu-like HTML，不包含用户私有素材。

---

## 9. 当前推荐路由

```text
普通医学长文
→ canghe-markdown-to-html

光愈在线式学术长文（非访谈）
→ 读取本 layout profile
→ 正文 16px / 1.85 为默认基线
→ 优先 section-heading-card
→ 数据类内容优先论文式统计图
→ 选择 canghe / xiaohu 合适主题并输出微信 inline HTML

专家访谈 / Q&A（普通）
→ article.md 使用 :::intro / :::dialogue
→ xiaohu interview 主题

光愈在线式头像访谈
→ article.md 使用 :::intro / :::dialogue
→ xiaohu interview 主题
→ enhance_guangyu_dialogue.py + 用户真实头像 / Logo 映射
→ canghe-post-to-wechat
```

---

## 10. 发布前视觉 QA

当用户要求“像样稿 / 高还原 / 光愈在线式”时，发布前至少检查：

```text
[ ] 正文是否仍只有 14~15px 而显得偏小？默认应接近 16px
[ ] 一级章节是否有足够视觉重量，而不是简单文字 + 小色块？
[ ] section-heading-card 的编号、标题、留白和下边线是否清楚？
[ ] 标题过长时是否保持 20px+，允许换行而不是缩字？
[ ] 图注是否明显小于正文但仍可读？
[ ] References 是否与正文拉开层级？
[ ] 手机端 375~430px 宽度下是否仍有舒适边距？
[ ] 封面是否使用用户确认的深玫瑰红 / 暖红主色而非浅粉白？
[ ] 2.35:1 封面缩略图中标题是否仍可读？
[ ] 未虚构审批号、责任编辑、专家身份、品牌 Logo 或产品资产？
```

若浏览器预览漂亮但微信草稿箱显示明显变形，应以**微信草稿箱 / 手机端真机预览**为准调整，不以桌面浏览器截图作为最终验收。

---

## 11. 后续扩展边界

如果继续提高还原度，只补缺失的**品牌组件**，不重写 Markdown / 微信 HTML 引擎：

```text
brand-follow
section-heading-card postprocessor（若 upstream 无法稳定实现）
summary-chip
end-divider
```

原则：

1. 先确认 upstream 是否已有等价能力；
2. 缺失时再做独立、可测试的小型后处理组件；
3. 每个组件只接收已完成内容和真实品牌素材，不负责医学写作、事实生产、配图生成或微信发布；
4. 不复制用户提供的原始 HTML、图片、SVG 或第三方编辑器代码到公共仓库；
5. 不因为样本中某组件高频出现，就强制所有未来文章必须出现它。
