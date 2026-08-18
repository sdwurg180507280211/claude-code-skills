# wechat-medical-writer

面向医学类微信公众号/服务号的专业文章创作 Skill。

## 当前定位

第一版以妇科 / 宫颈疾病为领域包，覆盖 HPV、HSIL、CIN2/CIN3、生育力保护、风险分层、PDT/HAL-PDT 等主题。领域结构来自用户当前提供的医学课件包，但**原始 ZIP/PPT 不进入仓库**。

## 输入

可以是：

- 一个文章主题
- 用户上传的 ZIP / PPT / PDF / Word
- 指南 / 共识 / 论文
- 产品说明书 / 注册资料
- 既有文章或内部培训资料

## 输出

推荐每篇文章生成一个本地工作目录：

```text
article-workspace/
├── article.md
├── claim-ledger.json
├── source-map.md
└── review-notes.md
```

生成物属于运行时输出，不应提交到仓库。

## 资料模式

```text
source-only     只使用用户资料
source-first    用户资料优先（默认）
research-update 用户明确要求时补充/核验最新外部来源
```

## 与其他 Skill 的关系

```text
wechat-medical-writer
        ↓
article.md
        ↓
canghe-article-illustrator（可选配图）
        ↓
canghe-markdown-to-html（排版）
        ↓
canghe-post-to-wechat（公众号草稿箱）
```

本 Skill 不复制苍何的公众号发布逻辑。

## Claim Ledger 校验

```bash
python3 scripts/validate_claim_ledger.py /path/to/claim-ledger.json
```

## 测试

```bash
python3 -m unittest discover -s tests -v
python3 -m compileall -q scripts
```

## 私有资料

推荐把原始医学资料放在仓库外：

```text
~/medical-content-library/
└── cervical-health/
    ├── slides/
    ├── papers/
    ├── guidelines/
    ├── labels/
    └── notes/
```

不要把真实课件、内部资料、患者资料、未公开研究或产品内部材料提交到本公共仓库。
