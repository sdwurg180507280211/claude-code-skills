# Changelog

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
