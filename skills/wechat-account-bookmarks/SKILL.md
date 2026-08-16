---
name: wechat-account-bookmarks
description: 批量把微信公众号名称、历史文章 URL 或已知 biz 转换为可直接导入 Edge/Chrome 的公众号主页书签。优先复用 freestylefly 的 wechat-article-archive-skill 与 wechat-article-extractor-skill，不重复实现微信搜索、文章历史和复杂页面解析。适用于“恢复微信公众号快捷方式”“Excel 批量生成公众号书签”“公众号名称跳转主页”等任务；不绕过登录、验证码或微信风控。
---

# 微信公众号批量书签生成

## 定位

本 Skill 只负责“输入编排 + 公众号身份结果统一 + 浏览器书签输出”。

微信侧复杂能力直接复用上游：

- `freestylefly/wechat-article-archive-skill`：公众号精确名称 → `searchbiz` → `fakeid` → 历史文章列表。
- `freestylefly/wechat-article-extractor-skill`：文章 URL/HTML → `account_name` / `account_alias` / `account_id` / `account_biz`，并处理迁移、注销、屏蔽、频控等页面异常。

本 Skill 不再维护自己的微信后台搜索客户端或完整文章解析器。

## 解析优先级

始终按成本最低、身份最确定的顺序处理：

```text
输入 biz
  ↓ 没有
输入微信公众号文章 URL
  ↓ URL 本身没有 __biz
上游 wechat-article-extractor-skill
  ↓ 仍无身份线索
公众号名称
  ↓
上游 wechat-article-archive-skill
  ↓
fakeid + 候选文章
  ↓
必要时再调用 extractor
```

因此：

- 已知 `biz` 时不访问微信后台。
- URL 已含 `__biz` 时不安装/调用上游解析器。
- 只有纯名称输入才进入微信公众平台扫码搜索流程。
- 不做模糊匹配，不猜测相似公众号。

## 输入

支持 `.xlsx` / `.csv`。名称列必需；其余列可选并自动识别。

常见字段：

```text
快捷方式名称 | 文件夹结构 | URL | biz
```

自动识别的 URL 列包括：`URL`、`链接`、`公众号链接`、`文章链接`、`历史链接`。

自动识别的 biz 列包括：`__biz`、`biz`、`account_biz`。

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

书签默认目标：

```text
https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=<biz>&scene=124#wechat_redirect
```

## 身份状态与书签状态必须分开

不要把“拿到 biz”直接等价为“桌面浏览器已验证可打开”。

`identity_status` 主要包括：

- `resolved`
- `not_found`
- `biz_not_found`
- `session_expired`
- `rate_limited`
- `error`

`bookmark_status` 主要包括：

- `unverified`：已生成主页 URL，但没有额外请求验证。
- `direct_ok`：检测到明确公众号主页结构且名称匹配。
- `requires_wechat`：需要微信客户端环境。
- `verification`：出现安全验证/频控。
- `inactive`：注销/屏蔽。
- `migrated`：迁移提示。
- `http_error`
- `unknown`：HTTP 返回但无法证明是正常主页；禁止把它误报成成功。

只有 `identity_status=resolved` 且存在 `biz + homepage_url` 才算身份解析成功。

## 上游版本

默认第一次真正需要上游能力时，自动缓存并固定到经过本 Skill 验证的版本：

```text
wechat-article-archive-skill
4820880eb51de1f05683a1511657db3a8cea59d0

wechat-article-extractor-skill
d8f74b8946065e64537f1ad39f962dbed86da3c7
```

缓存目录默认：

```text
~/.cache/wechat-account-bookmarks/upstream/
```

extractor 为 Node.js 项目，首次使用会执行其自己的 `npm ci --omit=dev`。

也可以通过：

```text
--archive-repo
--extractor-repo
--no-upstream-bootstrap
```

指定已经存在的上游仓库，不自动下载。

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

如果 Excel 已有 URL：

```bash
python3 scripts/generate_bookmarks.py \
  --input /path/to/accounts.xlsx \
  --name-column 快捷方式名称 \
  --folder-column 文件夹结构 \
  --url-column URL \
  --output-dir output
```

如果已经有 `biz`：

```bash
python3 scripts/generate_bookmarks.py \
  --input accounts.csv \
  --biz-column biz \
  --output-dir output
```

## 先预览输入

不登录、不 clone 上游、不访问微信：

```bash
python3 scripts/generate_bookmarks.py \
  --input accounts.xlsx \
  --prepare-only \
  --output-dir output-preview
```

生成：

```text
input_normalized.csv
input_summary.json
```

可看到多少条能直接用 biz、多少条能先用 URL、多少条需要名称搜索。

## 小批量试跑

先跑 5 条：

```bash
python3 scripts/generate_bookmarks.py \
  --input accounts.xlsx \
  --max-items 5 \
  --output-dir output-test
```

纯名称记录首次会由上游 archive skill 生成微信公众平台二维码并要求正常扫码确认。登录态复用其默认缓存：

```text
~/.cache/wechat-article-archive/session.json
```

## 断点续跑

`state.json` 使用 v2 schema，并保存 identity fingerprint。

- 只改文件夹结构不会让已经解析的身份失效。
- 名称、URL、biz 发生变化时不会错误沿用旧身份结果。
- `--retry-unresolved`：重试未解析项。
- `--no-resume`：忽略旧 state，全部重跑。

遇到明确频控时停止后续微信请求并保留断点，不继续轰炸接口。

## 主页验证

默认不额外请求几百个 `profile_ext`，避免增加微信请求量：

```text
bookmark_status = unverified
```

需要时显式开启：

```bash
python3 scripts/generate_bookmarks.py ... --validate-homepage
```

验证逻辑采用保守原则：

> 只有检测到明确公众号主页结构且名称匹配才标记 `direct_ok`；无法确认时标记 `unknown`。

不要使用“HTTP 200 且没看到错误文本 = 成功”的判定。

## 输出校验

生成后运行：

```bash
python3 scripts/validate_output.py output
```

校验：

- resolved 行必须有 `biz + homepage_url`
- `homepage_url` 的 `__biz` 必须与 CSV 一致
- unresolved 清单必须与身份状态一致
- 每个已解析 biz 至少出现在一个浏览器书签中
- `run_summary.json` 与 CSV 计数一致

## 导入 Edge / Chrome

浏览器中选择“从收藏夹/书签 HTML 导入”，导入：

```text
output/bookmarks.html
```

## 安全边界

- 只处理用户有权访问的公开微信公众号信息。
- 只使用正常扫码获得的微信公众平台登录态。
- 不破解验证码、不伪造登录态、不绕过风控。
- 不提高并发来规避微信限制。
- 精确名称搜索失败时宁可 unresolved，不自动匹配相似结果。
- 上游发生频控或验证时立即停止/降级，而不是循环重试。
