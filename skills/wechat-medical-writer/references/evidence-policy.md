# Evidence Policy

## Evidence hierarchy

医学文章优先使用以下证据顺序：

1. 国家/地区监管资料、药品/医疗器械说明书、注册证相关公开资料
2. 权威指南、专家共识、学会正式文件
3. 系统评价 / Meta-analysis
4. 随机对照试验
5. 前瞻性/回顾性队列、病例对照研究
6. 机制/临床前研究
7. 叙述性综述、教材、专业解读
8. 企业培训课件、会议幻灯、内部资料

该层级不是“低等级证据不可用”，而是决定表述强度与是否需要进一步核验。

## Claim types

推荐使用以下 `claim_type`：

```text
indication
contraindication
dosage_or_procedure
efficacy
safety
prognosis
fertility
mechanism
guideline_recommendation
regulatory_status
comparative_claim
background_fact
```

## Verification status

```text
source_only      # 仅确认来源资料中存在该表述
verified         # 已与适当的一手/权威来源核对
conflicting      # 来源之间存在冲突
insufficient     # 支持不足
not_checked      # 尚未核验
```

## Public-use status

```text
ready            # 证据与表述均可进入公开稿
medical_review   # 需医学审核
compliance_review# 涉及产品/广告/监管敏感表述，需合规审核
hold             # 暂不进入公开稿
```

## 强制进入 Claim Ledger 的内容

以下内容即使来自用户 PPT，也必须进入 Claim Ledger：

- 所有具体百分比、样本量、OR/HR/RR、P 值、时间点
- “提高、降低、优于、显著、更安全、更有效”等比较性表述
- “唯一、首个、最佳、治愈、无痛、无风险”等绝对或高风险表述
- 适应证、禁忌证、治疗次数、时间、剂量、器械操作参数
- 指南/共识推荐等级或推荐语
- NMPA/FDA/EMA 等批准/认证/上市状态
- 疾病进展、复发、生育结局
- 患者可能据此改变治疗决策的结论

## 写作强度

证据不够强时降低措辞：

```text
证实 → 提示 / 支持
必然 → 可能 / 与...相关
治愈 → 缓解 / 应答 / 组织学改善（按研究终点）
无风险 → 未观察到 / 风险较低（需具体证据）
无痛 → 疼痛发生率/评分较低或与对照相近（若证据支持）
```

## 产品医学教育

产品相关内容必须把“疾病教育”和“产品事实”拆开。

产品事实优先以说明书、注册资料或正式临床研究为依据。企业培训 PPT 可以作为线索，但不能单独支撑以下结论：

- 唯一/首个
- 已获批某适应证
- 更安全/更有效
- 无创/无痛/无副作用
- 对某亚组疗效更佳
- 操作参数、治疗时长、取出时间等具体使用要求

若正式资料未提供，标记 `compliance_review` 或 `hold`。
