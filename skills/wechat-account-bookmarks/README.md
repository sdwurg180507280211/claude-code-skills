# WeChat Account Bookmarks Skill

批量把微信公众号名称、历史文章 URL 或已知 `biz` 转成 Microsoft Edge / Google Chrome 可导入的公众号主页书签。

## v2 的核心变化

这个 Skill 不再自己重复实现微信公众平台搜索和复杂文章解析。

它直接复用：

- `freestylefly/wechat-article-archive-skill`：公众号名称 → `searchbiz` → `fakeid` → 历史文章
- `freestylefly/wechat-article-extractor-skill`：文章 URL/HTML → `account_biz`、公众号名称、微信号、迁移/注销/频控等状态

本 Skill 自己只维护：

```text
Excel / CSV 输入
→ 解析优先级编排
→ 统一身份结果
→ profile_ext 主页 URL
→ bookmarks.html
→ 状态/断点/输出校验
```

## 解析优先级

```text
已有 biz
→ 直接生成主页

没有 biz，但有文章 URL
→ URL 自带 __biz：直接使用
→ URL 无 __biz：调用上游 extractor

只有公众号名称
→ 调用上游 archive skill 精确搜索
→ fakeid + 候选文章
→ 必要时再调用 extractor
```

因此已有 URL/biz 的数据不会无意义地重新走微信后台搜索。

## 输入示例

```text
快捷方式名称    文件夹结构          URL                                      biz
财新            桌面 > 财经新闻    https://mp.weixin.qq.com/s?__biz=...     
证券时报        桌面 > 财经新闻                                             Mz...
iNature         桌面 > 科研学术                                             
```

名称列必需；URL 和 biz 都是可选增强信息。

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

真正需要名称搜索或复杂文章解析时，第一次运行会自动缓存固定版本的上游仓库：

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

extractor 需要 Node.js/npm，第一次使用会在它自己的缓存目录执行：

```bash
npm ci --omit=dev
```

如果本机已经有这两个仓库，可以传：

```text
--archive-repo /path/to/wechat-article-archive-skill
--extractor-repo /path/to/wechat-article-extractor-skill
```

## 先预览，不碰微信

```bash
python3 scripts/generate_bookmarks.py \
  --input accounts.xlsx \
  --prepare-only \
  --output-dir output-preview
```

会统计：

- 有多少条已有 biz
- 有多少条已有 URL
- 有多少条仍需要公众号名称搜索

## 先测试 5 条

```bash
python3 scripts/generate_bookmarks.py \
  --input accounts.xlsx \
  --max-items 5 \
  --output-dir output-test
```

只有纯名称记录才需要微信公众平台扫码。登录态直接复用苍何 archive skill 的缓存：

```text
~/.cache/wechat-article-archive/session.json
```

## 两类状态分开记录

`identity_status`：是否已经确定公众号身份。

```text
resolved
not_found
biz_not_found
session_expired
rate_limited
error
```

`bookmark_status`：主页 URL 在浏览器中的验证状态。

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

拿到 `biz` 不等于已经证明桌面浏览器可以直接进入主页。

默认不额外验证每个 `profile_ext`，所以通常为：

```text
bookmark_status = unverified
```

需要验证时：

```bash
python3 scripts/generate_bookmarks.py ... --validate-homepage
```

验证采用保守策略：无法明确证明是正常公众号主页时标记 `unknown`，不会把普通 HTTP 200 误报为成功。

## 主页 URL

```text
https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=<biz>&scene=124#wechat_redirect
```

## 断点续跑

`state.json` 使用 identity fingerprint：

- 只改文件夹，不重复解析公众号身份
- 名称、URL、biz 改变时，不复用旧身份结果
- `--retry-unresolved` 重试失败项
- `--no-resume` 全量重跑

遇到明确微信频控时会停止后续请求并保留断点。

## 输出校验

```bash
python3 scripts/validate_output.py output
```

校验 resolved、biz、主页 URL、unresolved 清单、书签和汇总统计是否一致。

## Edge / Chrome 导入

浏览器中选择“从收藏夹/书签 HTML 导入”，导入：

```text
output/bookmarks.html
```

## 安全边界

- 只处理公开微信公众号信息。
- 只使用用户正常扫码获得的公众平台登录态。
- 不破解验证码，不伪造 Cookie，不绕过微信风控。
- 不做模糊匹配；精确名称失败时进入 unresolved。
- 不为了速度提高微信侧并发。

## 测试

```bash
python3 -m unittest discover -s tests -v
```
