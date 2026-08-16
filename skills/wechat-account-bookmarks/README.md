# WeChat Account Bookmarks Skill

批量把微信公众号名称转换成可导入 Microsoft Edge / Google Chrome 的公众号主页书签。

## 能做什么

给它一个 Excel 或 CSV：

```text
快捷方式名称        文件夹结构
财新                桌面 > 财经新闻
证券时报            桌面 > 财经新闻
iNature             桌面 > 科研学术
```

工具会按下面的链路处理：

```text
公众号名称
→ 微信公众平台精确搜索
→ fakeid
→ 最近文章
→ __biz
→ 公众号 profile_ext 主页
→ bookmarks.html
```

输出：

```text
output/
├── bookmarks.html
├── wechat_accounts.csv
├── unresolved.csv
├── redirect-map.json
├── run_summary.json
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

首次正式解析会弹出微信公众平台登录二维码。扫码确认后开始串行处理。

### 先只检查输入（不登录微信）

```bash
python3 scripts/generate_bookmarks.py \
  --input examples/accounts.csv \
  --prepare-only \
  --output-dir output-preview
```

会生成 `input_normalized.csv` 和 `input_summary.json`，用于确认名称数量与目录结构。

### 先测试 5 条

```bash
python3 scripts/generate_bookmarks.py \
  --input /path/to/accounts.xlsx \
  --sheet 前面区域 \
  --max-items 5 \
  --output-dir output-test
```

## 重要说明

1. **输入已经被视为微信公众号名称**，工具不会混入视频号搜索逻辑。
2. 只接受 `nickname` 与输入名称完全一致的公众号搜索结果。
3. 不做模糊纠错，不猜测相似名称。
4. 主页 URL 使用：

   ```text
   https://mp.weixin.qq.com/mp/profile_ext?action=home&__biz=<biz>&scene=124#wechat_redirect
   ```

5. `profile_ext` 在普通桌面浏览器中可能要求微信环境或触发验证。为降低批量请求量，默认不额外验证；需要时加 `--validate-homepage`。
6. 微信接口存在频率限制，默认单线程并在公众号之间等待 1.5 秒。不要为了追求速度开高并发。
7. 批量搜索需要能正常扫码登录微信公众平台；本工具不会绕过登录、验证码或风控。

## 常用参数

```text
--input PATH                   输入 .xlsx 或 .csv
--sheet NAME                   Excel Sheet，默认第一个
--name-column NAME             名称列，默认自动识别
--folder-column NAME           文件夹列，默认自动识别
--output-dir DIR               输出目录，默认 output
--root-folder NAME             浏览器根收藏夹，默认 微信公众号
--strip-folder-prefix NAME     默认移除“桌面”这一层
--delay SECONDS                每个公众号之间等待，默认 1.5
--max-items N                  只处理前 N 个唯一名称
--validate-homepage            额外验证 profile_ext；默认关闭
--prepare-only                 只检查/规范化输入，不登录微信
--retry-unresolved             断点续跑时重试失败项
--no-resume                    忽略 state.json 全部重跑
```

## Edge 导入

Edge → 收藏夹 → 导入浏览器数据 → 从收藏夹/书签 HTML 导入 → 选择：

```text
output/bookmarks.html
```

开启 Edge 同步后，收藏夹可以同步到 Android Edge。

## 为什么保存 `biz`

公众号名称是检索入口；`fakeid` 用于公众平台后台查询；`__biz` 才是生成公众号主页 URL 的关键身份字段。因此 `wechat_accounts.csv` 会长期保存 `biz` 和备用文章 URL，方便以后重新生成书签或检查改名/迁移。

## 测试

离线测试不访问微信：

```bash
python3 -m unittest discover -s tests -v
```
