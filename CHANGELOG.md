# Changelog

## 2026-08-18

### Added
- `wechat-medical-writer`：面向医学类微信公众号/服务号的专业写作 Skill，支持 `source-only` / `source-first` / `research-update` 三种资料模式，要求关键医学结论进入 Claim Ledger。
- `wechat-medical-writer/references/domains/cervical-health.md`：第一版妇科/宫颈疾病领域包，覆盖 HPV、HSIL、CIN2/CIN3、生育力保护、风险分层与 PDT/HAL-PDT 等主题结构；不包含用户上传课件原件。
- `wechat-medical-writer/scripts/validate_claim_ledger.py`：离线校验医学 Claim Ledger 的字段、来源类型、核验状态和公开使用状态。
- `wechat-medical-writer/tests/test_claim_ledger.py`：覆盖有效 Claim、重复 ID、模型推断直接发布、未核验直接发布与缺少来源引用等规则。

### Changed
- Marketplace 增加 `wechat-medical-writer`，版本更新为 `1.4.0`。
- GitHub Actions 增加医学写作 Skill 的脚本编译和离线测试。
- 仓库文档明确：用户原始医学 ZIP/PPT/PDF、内部培训材料、患者资料和未公开研究默认不提交公共仓库。

## 2026-08-17

### Added
- `wechat-android-shortcuts`：从浏览器书签 Skill 中拆出的独立 Android 真机自动化 Skill，通过 ADB + 微信 UI + macOS Vision OCR 调用微信官方“添加到桌面”。
- `wechat-android-shortcuts/tests/test_core.py`：离线覆盖设备列表解析、名称匹配、候选排序、Activity 解析和输入法恢复逻辑。
- `wechat-ios-shortcuts`：把公众号名称 + HTTP/HTTPS 目标 URL 批量生成 Apple Web Clip `.mobileconfig`，用于 iPhone/iPad 主屏幕图标；可直接读取 `wechat-account-bookmarks` 输出的 `wechat_accounts.csv`。
- `wechat-ios-shortcuts/tests/test_generate_webclips.py`：离线覆盖输入列识别、重复/无效 URL 过滤、多 Web Clip payload 和 PNG 图标嵌入。

### Changed
- `wechat-account-bookmarks` 回归单一职责，只负责公众号身份 / 文章 URL / `biz` → Edge / Chrome 主页或文章书签。
- `wechat-android-shortcuts/scripts/batch_add_wechat.py` 收敛为唯一批量入口，删除拆分时遗留的 `_batch_add_wechat_impl.py` 包装层。
- Android 批量脚本不再包含开发机绝对路径、固定设备 serial 或固定搜狗输入法；单设备自动选择 serial，多设备要求 `ANDROID_SERIAL`。
- Android 批量脚本运行前记录系统当前默认输入法，并在正常结束或异常后通过 `try/finally` 恢复原输入法。
- GitHub Actions 新增 `wechat-android-shortcuts` 离线测试，并增加 `wechat-ios-shortcuts` 依赖安装、编译和离线测试。

## 2026-08-16

### Added
- `wechat-account-bookmarks`: 批量解析微信公众号名称、历史文章 URL 或已知 `biz`，生成公众号主页 URL 与 Edge/Chrome 可导入的 `bookmarks.html`。
- `wechat-account-bookmarks/scripts/validate_output.py`：校验 identity、biz、主页 URL、书签和汇总输出契约。
- `.claude-plugin/marketplace.json`，支持按 Skill bundle 安装。
- GitHub Actions + `scripts/validate_skills.py` 仓库结构校验。
- `CONTRIBUTING.md` 与 `CLAUDE.md` 维护规范。

### Changed
- `wechat-account-bookmarks` v2 改为上游优先架构：直接复用 `freestylefly/wechat-article-archive-skill` 的公众号发现能力和 `freestylefly/wechat-article-extractor-skill` 的复杂微信页面解析能力，不再重复维护微信搜索/解析实现。
- 公众号身份解析优先级调整为 `input biz > input article URL > upstream extractor > upstream archive search`。
- 拆分 `identity_status` 与 `bookmark_status`；主页无法明确证明正常时标记 `unknown`，不再把普通 HTTP 200 当成成功。
- `state.json` 升级为 v2 schema，并使用 identity fingerprint，避免名称/URL/biz 变化后误复用旧结果。
- 重写根 README，使安装方式、目录结构和 Skill 清单与真实仓库保持一致。
- 收窄 `china-proxy` 与 `github-kb` 的触发范围，减少误触发和机器相关假设。

### Removed
- `wechat-account-bookmarks/scripts/wechat_mp.py`：删除与苍何上游重复的微信公众平台搜索和文章解析实现。
- 根目录 `install.sh`：硬编码 Skill 列表已经出现遗漏，改用标准 Skills CLI / Claude Code Plugin Marketplace。
- `skills/skill-creator/`：属于体积较大的通用上游 Skill，不再在个人仓库复制维护；需要时直接使用维护中的上游版本。
