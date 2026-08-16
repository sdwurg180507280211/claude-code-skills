---
name: wechat-account-bookmarks
description: 批量把微信公众号名称解析为稳定身份（fakeid / __biz），生成可直接导入 Edge/Chrome 的公众号主页书签。适用于“批量恢复微信公众号快捷方式”“把公众号 Excel 生成浏览器书签”“公众号名称跳转主页”等任务。只处理用户有权访问的公开公众号信息，不绕过验证码、登录限制或微信风控。
---

# 微信公众号批量书签生成

## 目标

把一批已经确认属于“微信公众号”的名称转换为：

1. 公众号身份数据库 `wechat_accounts.csv`
2. 公众号主页书签 `bookmarks.html`
3. 未解析清单 `unresolved.csv`
4. 机器可读映射 `redirect-map.json`
5. 运行摘要 `run_summary.json`

书签默认指向：

```text
https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=<biz>&scene=124#wechat_redirect
```

## 核心原则

- 公众号名称是检索键。
- `fakeid` 只作为微信公众平台后台的采集过程 ID。
- `__biz` 是长期身份锚点。
- 不做模糊匹配，不猜测相似公众号。
- 精确名称搜不到时写入 `unresolved.csv`。
- 不绕过验证码、登录限制或风控。
- 批量任务串行执行并限速。

## 首选工作流

### 1. 安装依赖

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Windows PowerShell：

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 2. 从 Excel 生成书签

对常见的“快捷方式名称 / 文件夹结构”格式：

```bash
python3 scripts/generate_bookmarks.py \
  --input /path/to/accounts.xlsx \
  --sheet 前面区域 \
  --name-column 快捷方式名称 \
  --folder-column 文件夹结构 \
  --output-dir output
```

首次需要微信公众平台二维码登录。登录态默认缓存在：

```text
~/.cache/wechat-account-bookmarks/session.json
```

### 2.1 先检查输入，不登录微信

```bash
python3 scripts/generate_bookmarks.py \
  --input examples/accounts.csv \
  --prepare-only \
  --output-dir output-preview
```

这一步只做去重和目录规范化，输出 `input_normalized.csv` 与 `input_summary.json`。

### 3. 小批量试跑

正式跑几百个名称之前先测试 5 个：

```bash
python3 scripts/generate_bookmarks.py \
  --input /path/to/accounts.xlsx \
  --sheet 前面区域 \
  --max-items 5 \
  --output-dir output-test
```

确认 `wechat_accounts.csv` 和 `bookmarks.html` 后再跑全量。

### 4. CSV 也可直接输入

```bash
python3 scripts/generate_bookmarks.py \
  --input accounts.csv \
  --name-column 公众号名称 \
  --folder-column 分类 \
  --output-dir output
```

## 处理流程

```text
输入 Excel / CSV
  ↓
读取公众号名称和目录
  ↓
微信公众平台 searchbiz 精确搜索 nickname
  ↓
获得 fakeid
  ↓
读取该公众号最近文章
  ↓
从文章 URL / 页面解析 __biz
  ↓
生成 profile_ext 主页 URL
  ↓
轻量验证（不绕过登录/验证码）
  ↓
wechat_accounts.csv + bookmarks.html + unresolved.csv
```

## 状态说明

常见 `status`：

- `homepage_ok`：普通 HTTP 验证未发现明显阻断。
- `homepage_requires_wechat`：页面提示需要微信客户端环境。
- `homepage_verification`：出现验证码/环境验证/频控提示。
- `homepage_http_error`：主页 HTTP 状态异常。
- `resolved_unverified`：已拿到 `biz`，但跳过了主页验证。
- `not_found`：精确公众号名称未找到。
- `no_article`：找到公众号但没有取得可用文章。
- `biz_not_found`：文章存在但没能提取 `__biz`。
- `error`：其他错误。

默认不对每个 `profile_ext` 再发一次 HTTP 验证请求；已拿到 `biz` 时状态为 `resolved_unverified`，仍会生成主页书签。若需要额外验证，运行时加 `--validate-homepage`。实际 Edge/手机端表现以实机为准。

## 输出字段

`wechat_accounts.csv` 至少包含：

```text
original_name,current_name,alias,fakeid,biz,homepage_url,
fallback_article_url,fallback_article_title,folder,status,
validation_http_status,validation_final_url,error,last_verified_at
```

## 目录转换

输入：

```text
桌面 > 财经新闻
```

默认输出为：

```text
微信公众号 > 财经新闻
```

可用 `--strip-folder-prefix` 调整要移除的第一层目录。

## 导入 Edge / Chrome

生成完成后，在浏览器中选择“导入收藏夹/书签 HTML”，导入：

```text
output/bookmarks.html
```

## 断点续跑

运行状态保存在：

```text
output/state.json
```

再次运行相同输入时，已经成功解析出 `biz` 的公众号默认跳过，避免重复请求。

要重新尝试未解析项：

```bash
python3 scripts/generate_bookmarks.py ... --retry-unresolved
```

要完全重跑：

```bash
python3 scripts/generate_bookmarks.py ... --no-resume
```

## 安全边界

- 只使用用户正常扫码获得的微信公众平台登录态。
- 不破解验证码。
- 不伪造登录态。
- 不并发轰炸微信接口。
- 遇到验证/风控时记录状态并停止该路径。
- 搜索结果不精确时宁可 unresolved，不自动选相似名称。

## 参考实现

设计思路参考：

- `freestylefly/canghe-skills` 中的微信公众号文章解析能力。
- `freestylefly/wechat-article-archive-skill` 的 `discover_account_articles.py`：名称 → `fakeid` → 文章列表。
- `freestylefly/wechat-extract`：文章 → 公众号身份信息。

本 Skill 自包含完成书签生成，不要求安装上述仓库。
