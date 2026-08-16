# WeChat Account Bookmarks Skill

批量把微信公众号名称、历史文章 URL 或已知 `biz` 转成 Microsoft Edge / Google Chrome 可导入的公众号书签。最终书签优先指向公众号主页；无法形成主页但已经确认到该公众号文章时，可直接以文章 URL 作为可点击目标。

## 架构

微信侧复杂能力直接复用：

- `freestylefly/wechat-article-archive-skill`：公众号精确名称 → `searchbiz` → `fakeid` → 历史文章
- `freestylefly/wechat-article-extractor-skill`：文章 URL/HTML → `account_biz`、公众号名称、微信号、迁移/注销等状态

`freestylefly/canghe-skills` 中的 `skills/canghe-wechat-article-extractor` 本身就是 submodule，并指向同一份 extractor 实现。本 Skill 不复制维护微信解析器，只维护 Excel/CSV 输入、结果编排、书签输出、状态与校验。

## 解析优先级

```text
已有 biz
→ 直接构造主页 target
→ 名称本身标记为“未通过文章核验”

已有文章 URL
→ 调用上游 extractor 核对文章所属公众号
→ 名称一致：优先生成主页；没有 biz 时使用文章作为 target
→ 名称不一致/无法核对：pending_review，不生成错误书签

只有公众号名称
→ 上游 archive skill 精确搜索
→ fakeid + 候选文章
→ 有 biz：主页 target
→ 没有 biz 但有精确账号来源的文章：文章 target
```

因此“拿不到主页”不再自动等于失败；只要已经确认到该公众号的可用文章，就可以生成文章书签。

## 输入示例

```text
快捷方式名称    文件夹结构          URL                                      biz
财新            桌面 > 财经新闻    https://mp.weixin.qq.com/s?__biz=...     
证券时报        桌面 > 财经新闻                                             Mz...
iNature         桌面 > 科研学术                                             
```

名称列必需；URL 和 biz 都是可选增强信息。

## 环境要求

```text
Python 3.10+
Git
Node.js + npm（需要文章 extractor 时）
```

Python 依赖：

```bash
pip install -r requirements.txt
```

## 输出

```text
output/
├── bookmarks.html
├── wechat_accounts.csv
├── unresolved.csv
├── bookmark_review.csv
├── redirect-map.json
├── run_summary.json
├── input_meta.json
└── state.json
```

关键字段新增：

```text
target_type      homepage / article
target_url       最终真正写入浏览器书签的 URL
fallback_status  present / missing
error_code       可机器处理的失败/待复核原因
```

`bookmark_review.csv` 会包含所有未验证书签，以及缺少备用文章的已解析记录；默认不会再出现“全部 unverified 但复核文件为空”的情况。

## 快速开始

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python3 scripts/generate_bookmarks.py \
  --input /path/to/accounts.xlsx \
  --sheet 前面区域 \
  --name-column 快捷方式名称 \
  --folder-column 文件夹结构 \
  --output-dir output
```

如果 Excel 中已有 URL：

```bash
python3 scripts/generate_bookmarks.py \
  --input /path/to/accounts.xlsx \
  --name-column 快捷方式名称 \
  --folder-column 文件夹结构 \
  --url-column URL \
  --output-dir output
```

如果已有 biz：

```bash
python3 scripts/generate_bookmarks.py \
  --input accounts.csv \
  --biz-column biz \
  --output-dir output
```

## 上游依赖

第一次真正需要上游能力时，会自动缓存固定版本：

```text
~/.cache/wechat-account-bookmarks/upstream/
```

固定版本：

```text
wechat-article-archive-skill
4820880eb51de1f05683a1511657db3a8cea59d0

wechat-article-extractor-skill
d8f74b8946065e64537f1ad39f962dbed86da3c7
```

首次 clone 后会强制 checkout 到固定 commit，避免 `--no-checkout` 留下空工作区。

extractor 首次使用会在自己的缓存目录执行：

```bash
npm ci --omit=dev
```

也可以传本地仓库：

```text
--archive-repo /path/to/wechat-article-archive-skill
--extractor-repo /path/to/wechat-article-extractor-skill
```

## 先预览

```bash
python3 scripts/generate_bookmarks.py \
  --input accounts.xlsx \
  --prepare-only \
  --output-dir output-preview
```

预览不会登录微信或下载上游。

## 状态

`identity_status`：

```text
resolved
pending_review
not_found
no_article
biz_not_found
session_expired
rate_limited
inactive
migrated
error
```

`bookmark_status`：

```text
unverified
direct_ok
requires_wechat
verification
inactive
migrated
http_error
unknown
```

常见 `error_code`：

```text
article_name_mismatch
article_name_unavailable
article_identity_unverified
exact_name_unresolved
exact_name_not_found
no_article
session_expired
upstream_error
```

名称与文章身份不一致时不会静默绑定，而是进入 `pending_review`。

## target 与 fallback

最终写入 `bookmarks.html` 的不是固定的 `homepage_url`，而是：

```text
target_url
```

规则：

```text
有可信 biz → target_type=homepage → target_url=homepage_url
没有主页但已有可信文章 → target_type=article → target_url=fallback_article_url
```

已知 biz 可以完全离线生成主页书签，但因为没有自动获取备用文章，会标记：

```text
fallback_status=missing
```

并进入 `bookmark_review.csv`，不会被误认为已经完全验收。

## 主页 URL

```text
https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=<biz>&scene=124#wechat_redirect
```

## 断点续跑

`state.json` 当前 schema 为 v3，并保存 identity fingerprint：

- 只改文件夹结构不会让身份缓存失效
- 名称、URL、biz 变化时不会错误复用旧身份
- `--retry-unresolved`：重试未解析项
- `--no-resume`：全部重跑

## 输出校验

```bash
python3 scripts/validate_output.py output
```

校验包括：

- resolved 必须存在有效 `target_type + target_url`
- homepage target 的 `__biz` 必须与 `biz` 一致
- article target 必须与 `fallback_article_url` 一致
- unresolved 记录不能偷偷进入书签
- `bookmarks.html` 与已解析 target 一致
- `run_summary.json` 与 CSV 计数一致

## Edge / Chrome 导入

浏览器中选择“从收藏夹/书签 HTML 导入”，导入：

```text
output/bookmarks.html
```

## 安全边界

- 只处理公开微信公众号信息。
- 不做模糊匹配，不猜测相似公众号。
- URL 与名称不一致时进入人工复核。
- 不破解验证码，不伪造 Cookie，不绕过微信风控。

## 测试

```bash
python3 -m unittest discover -s tests -v
```

测试覆盖 CSV、XLSX、书签 target、URL 名称一致/不一致、已知 biz 离线路径，以及首次 clone 默认 HEAD 等于固定 commit 时工作区仍能正确 checkout 的回归场景。
