# WeChat Account Bookmarks Skill

批量把微信公众号名称、历史文章 URL 或已知 `biz` 转成 Microsoft Edge / Google Chrome 可导入的公众号书签。最终书签优先指向公众号主页；无法形成主页但已经确认到该公众号文章时，可直接以文章 URL 作为可点击目标。也支持通过 `--prefer-article` / `--target article` / 输入列 `目标类型` 强制把书签指向公众号文章，适合浏览器无法打开公众号主页的场景。

此外还支持通过 ADB 在 Android 手机桌面上用微信官方“添加到桌面”流程创建/检查微信公众号快捷方式，详见 `references/adb-desktop-shortcuts.md`。

## 架构

微信侧复杂能力直接复用：

- `freestylefly/wechat-article-archive-skill`：公众号精确名称 → `searchbiz` → `fakeid` → 历史文章
- `freestylefly/wechat-article-extractor-skill`：文章 URL/HTML → `account_biz`、公众号名称、微信号、迁移/注销等状态

`freestylefly/canghe-skills` 中的 `skills/canghe-wechat-article-extractor` 本身就是 submodule，并指向同一份 extractor 实现。本 Skill 不复制维护微信解析器，只维护 Excel/CSV 输入、结果编排、书签输出、状态与校验。

## Android 桌面快捷方式（ADB）

需要直接在 Android 手机桌面创建/检查微信公众号图标时，使用微信官方“添加到桌面”流程，而不是伪造 ShortcutInfo：

```text
打开微信
→ 搜索公众号（ADB 输入拼音或 ADBKeyBoard 中文）
→ 进入公众号主页
→ 如未关注，先“关注服务号/关注公众号”
→ 关注后微信会进入聊天界面
→ 点右上角头像回到简介页
→ 再点右上角“•••”
→ “设置”
→ “添加到桌面”
→ 返回桌面验证 Chat_User=gh_...
```

微信界面屏蔽 `uiautomator dump`，因此用截图 + macOS Vision OCR 定位按钮。

常见操作技巧：

- 搜索框有旧文字时，点右侧 `x` 清空，不需要返回；
- 默认搜索结果没有公众号时，小幅向左滑动搜索框下方的筛选行，露出“账号”（不要大幅滑，否则会滑过头）；
- 关注后进入聊天界面，点右上角头像回到简介页，再点“•••”；
- 已关注的公众号直接点右上角“•••”，不用再点关注；
- 批量连续添加时，添加完一个直接继续搜索下一个，最后再统一核对；
- 账号筛选也找不到时，大概率已失效/改名/未收录，跳过即可；
- 搜索优先级：公众号 > 视频号 > 小程序；小程序优先级最低但会尝试添加；
- 小程序添加流程：进入小程序 → 右上角“•••” → 底部“转发给朋友”行 → 向左滑动 → 右侧“添加到桌面/添加到” → 点击 → 右下角返回；
- 输入后直接点顶部“搜索”按钮，不要点键盘搜索键；
- 账号筛选里点“不限”通常能让公众号显示在最上面；
- 点“账号”后，第一个结果不一定是公众号，可能是视频号/小程序；公众号可能在下面，优先找带“公众号/服务号/媒体”标签的结果；
- 公众号名称不全时用模糊匹配（前缀/关键字），不要要求完整名称完全一致；模糊匹配只用于找候选，进入资料页后必须二次验证完整名称/主体/简介/gh_ ID 或 URL/biz，验证不通过不添加；
- 有些视频号右上角“•••”没有“设置”，无法添加到桌面，直接跳过；
- 如果进入视频号资料页但有“公众号：xxx”入口，先点入口进入真正公众号设置页；
- Excel 里的名称可能是小程序/视频号；小程序优先级最低但会尝试添加，视频号优先级高于小程序但低于公众号；
- 不要用一条 `adb shell` 串联“输入框 + 清空 + 输入广播”，中文输入会不稳定，应分步执行；
- “添加到桌面”的 y 坐标见过 `812`、`1017`、`1221`、`1360`，必须 OCR 确认。

已知限制：MIUI 通过 ADB 模拟长按拖动创建文件夹目前不可靠，建文件夹建议手动操作；小程序优先级最低，但会尝试添加。

## 批量脚本使用

```bash
python3 scripts/batch_add_wechat.py 公众号1 公众号2 公众号3 ...
```

跨设备时可通过环境变量覆盖：

```bash
ADB_PATH=/path/to/adb \
ANDROID_SERIAL=<serial> \
OCR_SCRIPT=/path/to/ocr_wechat.swift \
python3 scripts/batch_add_wechat.py 公众号1 公众号2 ...
```

脚本运行前，手机应停在**微信内、上一个公众号的设置页或简介页**（保证按一次返回能回到简介页，并能点右上角 Q 搜索）。

脚本会自动：

```text
返回 → 点 Q → 输入 → 点匹配项 → 切“账号” → 找公众号/服务号/媒体
→ 关注（已关注则跳过）→ 进入设置 → 添加到桌面
→ 继续下一个
```

完整命令和脚本：

```text
references/adb-desktop-shortcuts.md
scripts/ocr_wechat.swift
scripts/batch_add_wechat.py
```

## 解析优先级

```text
用户指定 article（--prefer-article / 目标类型=article）
→ 即使有 biz，也生成文章 target

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
快捷方式名称    文件夹结构          URL                                      biz        目标类型
财新            桌面 > 财经新闻    https://mp.weixin.qq.com/s?__biz=...               article
证券时报        桌面 > 财经新闻                                             Mz...
iNature         桌面 > 科研学术                                             
```

名称列必需；URL、biz、目标类型都是可选增强信息。`目标类型` 取值 `auto` / `homepage` / `article`，也自动识别 `target_type`、`书签目标` 等列名。

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

## 强制生成文章书签

浏览器无法打开公众号主页时，可以用 `--prefer-article` 或 `--target article` 让所有书签指向公众号文章：

```bash
python3 scripts/generate_bookmarks.py \
  --input accounts.xlsx \
  --prefer-article \
  --output-dir output-article
```

也可以在输入表加 `目标类型` 列，值填 `article`，按行控制。`--target article` 是全局默认，行内 `auto` 会继承全局值，行内显式 `article` / `homepage` 优先生效。

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
no_homepage
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
用户指定 article → target_type=article → target_url=fallback_article_url（即使有 biz）
用户指定 homepage → target_type=homepage → target_url=homepage_url
有可信 biz（auto） → target_type=homepage → target_url=homepage_url
没有主页但已有可信文章（auto） → target_type=article → target_url=fallback_article_url
```

强制 `article` 但没有可用文章 URL 时，不降级生成主页书签，而是标记 `no_article`；强制 `homepage` 但没有主页时标记 `biz_not_found` / `no_homepage`。

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
- 名称、URL、biz、目标类型变化时不会错误复用旧身份/旧目标
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
