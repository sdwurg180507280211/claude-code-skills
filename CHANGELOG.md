# Changelog

## 2026-08-16

### Added
- `wechat-account-bookmarks`: 批量解析微信公众号名称，获取 `fakeid` / `__biz`，生成公众号主页 URL 与 Edge/Chrome 可导入的 `bookmarks.html`。
- `.claude-plugin/marketplace.json`，支持按 Skill bundle 安装。
- GitHub Actions + `scripts/validate_skills.py` 仓库结构校验。
- `CONTRIBUTING.md` 与 `CLAUDE.md` 维护规范。

### Changed
- 重写根 README，使安装方式、目录结构和 Skill 清单与真实仓库保持一致。
- 收窄 `china-proxy` 与 `github-kb` 的触发范围，减少误触发和机器相关假设。

### Removed
- 根目录 `install.sh`：硬编码 Skill 列表已经出现遗漏，改用标准 Skills CLI / Claude Code Plugin Marketplace。
- `skills/skill-creator/`：属于体积较大的通用上游 Skill，不再在个人仓库复制维护；需要时直接使用维护中的上游版本。
