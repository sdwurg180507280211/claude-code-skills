# wechat-ai-model-writer

把每日 AI 模型 / API 价格 / 免费额度 / 高性价比渠道情报，编辑成适合微信公众号发布的科技情报内容。

## 适合什么

典型输入是定时任务 **“AI模型省钱情报”** 的结果。Skill 会先判断应该做成：

- `daily`：AI 模型省钱日报；
- `breaking`：重大模型发布、降价或渠道变化的单篇深度稿；
- `weekly`：一周模型性价比榜。

然后补齐价格、渠道、风险等结构化字段，再把通用研究与正文写作交给同仓库 `content-research-writer`。

## 不做什么

- 不用于医学公众号；医学内容继续使用 `wechat-medical-writer`。
- 不把每日采集到的 5+2 条情报机械拼成文章。
- 不把媒体转述的价格当成官方价格。
- 不推荐盗号、共享 API Key、来源不明密钥或规避地区限制的渠道。
- 不为了排版效果伪造价格、性能分数或排行榜数据。

## 默认日报结构

```text
标题
↓
一句话导语
↓
今日最省钱结论（1～3 个）
↓
TOP 模型信息卡
↓
价格 / 能力对比表
↓
其他值得关注的变化
↓
今天怎么选
↓
风险提示
↓
信息来源
```

模板：`templates/daily.md`

## 设计资料

- `references/intelligence-contract.md`：原始情报进入公众号之前应具备的字段、价格归一化和渠道风险规则。
- `references/layouts/ai-savings-daily.md`：日报视觉 Token、结论卡、模型卡、价格表、风险卡和手机窄屏排版规范。
- `templates/daily.md`：日报内容骨架。
- `templates/daily.html`：可供 formatter / HTML 生成阶段参考的基础组件骨架；内容中的占位符必须在发布前替换，不应直接发布模板文件。

## 推荐工作流

```text
AI模型省钱情报
→ wechat-ai-model-writer（选题/事实结构）
→ content-research-writer（研究/正文）
→ 数据表/信息卡
→ 微信 HTML formatter
→ 人工复核
→ 发布
```

如果当日存在足以改变模型选择的重大事件，优先升级为 `breaking`，不要为了保持日报形式稀释重点。
