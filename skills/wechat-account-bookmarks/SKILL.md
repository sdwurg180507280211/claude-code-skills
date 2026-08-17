---
name: wechat-account-bookmarks
description: 批量把微信公众号名称、历史文章 URL 或已知 biz 转换为可直接导入 Edge/Chrome 的公众号主页或文章书签；也支持通过 ADB 在 Android 手机桌面上用微信官方“添加到桌面”流程创建/检查微信公众号快捷方式。优先复用 freestylefly 的 wechat-article-archive-skill 与 wechat-article-extractor-skill，不重复实现微信搜索、文章历史和复杂页面解析。适用于“恢复微信公众号快捷方式”“Excel 批量生成公众号书签”“公众号名称跳转主页或文章”“ADB 创建微信公众账号桌面图标”“检查桌面微信快捷方式内部结构”等任务；不绕过登录、验证码或微信风控。
---

# 微信公众号批量书签生成

## 两种工作模式

1. **浏览器书签模式（默认）**：Excel/CSV → Edge/Chrome 可导入的 `bookmarks.html`。
2. **Android 桌面快捷方式模式**：通过 ADB 操作微信官方“添加到桌面”，在手机桌面生成真实公众号图标。

模式 2 的完整流程见 `references/adb-desktop-shortcuts.md`，OCR 脚本见 `scripts/ocr_wechat.swift`，批量连续添加脚本见 `scripts/batch_add_wechat.py`。

## 定位

本 Skill 负责两条输出链路：

- 浏览器书签：输入编排 + 公众号身份结果统一 + `bookmarks.html` 输出。
- Android 桌面图标：通过 ADB 驱动微信官方“添加到桌面”，并验证 `Chat_User=gh_...`。

微信侧复杂能力直接复用上游：

- `freestylefly/wechat-article-archive-skill`：公众号精确名称 → `searchbiz` → `fakeid` → 历史文章列表。
- `freestylefly/wechat-article-extractor-skill`：文章 URL/HTML → `account_name` / `account_alias` / `account_id` / `account_biz`，并处理迁移、注销、屏蔽等页面异常。

本 Skill 不维护自己的微信后台搜索客户端或完整文章解析器。

## 核心成功标准

不要把“拿到 `biz`”当作唯一成功标准。最终目标是得到一个已经与输入公众号身份对应的可点击目标：

```text
target_type = homepage | article
target_url  = 最终写入 bookmarks.html 的 URL
```

优先级：

```text
用户指定目标类型 article（--prefer-article / 目标类型=article）
→ 即使有 biz，也生成文章 target

可信 biz
→ 公众号主页 target

没有主页，但已有可信公众号文章
→ 文章 target
```

## 解析优先级

```text
输入 biz
  ↓ 没有
输入微信公众号文章 URL
  ↓
上游 wechat-article-extractor-skill 核对公众号名称
  ↓ 没有 URL
公众号名称
  ↓
上游 wechat-article-archive-skill 精确搜索
  ↓
fakeid + 候选文章
  ↓
必要时再调用 extractor
```

规则：

- 已知 `biz` 时不访问微信后台；只把它当身份锚点，不把 Excel 名称冒充成已核验的当前公众号名称。
- 文章 URL 即使自带 `__biz`，也要通过 extractor 核对文章所属公众号名称。
- URL 解析出的公众号名称与 Excel 名称不一致时：`identity_status=pending_review`，`error_code=article_name_mismatch`，不得生成错误书签。
- 纯名称路径仍要求上游 archive skill 做精确名称匹配，不做模糊猜测。
- 如果精确账号已经找到，且有可信文章 URL，但没有 `biz`，可以生成 `target_type=article` 的文章书签。
- 用户可通过 CLI `--target article` / `--prefer-article` 或输入列 `目标类型` 强制生成文章书签；指定 `article` 后即使已有 `biz` 也以文章 URL 为最终书签目标。
- 强制 `article` 但没有任何可用文章 URL 时，不降级生成主页书签，而是标记 `no_article` 进入未解析/复核。

## 输入

支持 `.xlsx` / `.csv`。名称列必需；其余列可选并自动识别。

常见字段：

```text
快捷方式名称 | 文件夹结构 | URL | biz | 目标类型
```

`目标类型` 可选值：`auto` / `homepage` / `article`，也自动识别 `target_type`、`书签目标` 等列名。

自动识别 URL 列：`URL`、`链接`、`公众号链接`、`文章链接`、`历史链接`。

自动识别 biz 列：`__biz`、`biz`、`account_biz`。

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

关键结果字段：

```text
original_name
current_name
fakeid
biz
homepage_url
fallback_article_url
target_type
target_url
identity_status
bookmark_status
fallback_status
resolved_by
error_code
error
```

`bookmark_review.csv` 必须包含：

- 所有 `bookmark_status != direct_ok` 的已解析书签，包括默认的 `unverified`；
- 所有 `fallback_status != present` 的已解析记录。

这样不能出现“大量主页从未验证，但复核清单为空”的假象。

## 状态

`identity_status` 主要包括：

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

`error_code` 用来区分具体原因，例如：

```text
article_name_mismatch
article_name_unavailable
article_identity_unverified
exact_name_unresolved
exact_name_not_found
no_article
no_homepage
session_expired
upstream_error
```

`bookmark_status` 主要包括：

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

## 上游版本

固定使用：

```text
wechat-article-archive-skill
4820880eb51de1f05683a1511657db3a8cea59d0

wechat-article-extractor-skill
d8f74b8946065e64537f1ad39f962dbed86da3c7
```

缓存目录：

```text
~/.cache/wechat-account-bookmarks/upstream/
```

首次使用 `git clone --no-checkout` 后必须显式 checkout 固定 commit；不能因为 `HEAD` 已等于目标 commit 就跳过 checkout，否则会留下空工作区。

extractor 需要 Node.js/npm，首次使用会执行：

```bash
npm ci --omit=dev
```

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

环境建议：

```text
Python 3.10+
Git
Node.js + npm
```

## 先预览输入

```bash
python3 scripts/generate_bookmarks.py \
  --input accounts.xlsx \
  --prepare-only \
  --output-dir output-preview
```

预览阶段不登录、不 clone 上游、不访问微信。

## 小批量试跑

正式处理大名单前先跑少量记录：

```bash
python3 scripts/generate_bookmarks.py \
  --input accounts.xlsx \
  --max-items 5 \
  --output-dir output-test
```

## 强制生成文章书签

浏览器无法打开公众号主页时，可以用 `--prefer-article` 或 `--target article` 让所有书签指向公众号文章：

```bash
python3 scripts/generate_bookmarks.py \
  --input accounts.xlsx \
  --prefer-article \
  --output-dir output-article
```

也可以在输入表加 `目标类型` 列，值填 `article`，按行控制。`--target article` 是全局默认，行内 `auto` 会继承全局值，行内显式 `article` / `homepage` 优先生效。

## 主页验证

默认不额外验证每个 `profile_ext`：

```text
bookmark_status = unverified
```

需要时显式开启：

```bash
python3 scripts/generate_bookmarks.py ... --validate-homepage
```

只有检测到明确公众号主页结构时才标记 `direct_ok`；无法确认时标记 `unknown`。

## 断点续跑

`state.json` schema 为 v3。

- 只改文件夹结构不会让身份缓存失效。
- 名称、URL、biz、目标类型变化时不复用旧身份/旧目标结果。
- `--retry-unresolved`：重试未解析项。
- `--no-resume`：全部重跑。

## 输出校验

```bash
python3 scripts/validate_output.py output
```

校验：

- `resolved` 必须有合法 `target_type + target_url`；
- homepage target 必须有一致的 `biz + homepage_url`；
- article target 必须等于 `fallback_article_url`；
- unresolved / pending_review 不得偷偷进入 `bookmarks.html`；
- `run_summary.json` 与 CSV 计数一致。

## 安全边界

- 只处理用户有权访问的公开微信公众号信息。
- 不破解验证码、不伪造登录态、不绕过风控。
- 不做模糊匹配。
- 名称与文章身份不一致时进入 `pending_review`，不要自动猜测。
