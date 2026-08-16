# Repository Guide

本仓库是自包含 Agent Skills 集合。

## 目录约定

- 每个 Skill 放在 `skills/<skill-name>/`。
- `SKILL.md` 必须存在，frontmatter 至少包含 `name` 与 `description`。
- 脚本、测试、示例、参考资料都放在对应 Skill 目录内。
- 不把运行结果、用户输入、Cookie、Token、session、二维码、缓存提交到仓库。

## 质量要求

1. Skill 的触发描述要具体，避免劫持无关任务。
2. 优先成熟依赖和简单实现，不为了未来功能增加额外兼容层。
3. 可确定验证的解析/转换能力应提供离线测试。
4. 新增或删除 Skill 时同步更新 `README.md`、`.claude-plugin/marketplace.json` 和 `CHANGELOG.md`。
5. 提交前运行 `python3 scripts/validate_skills.py`，并运行对应 Skill 的测试。

## WeChat Skill

`wechat-account-bookmarks` 只使用正常扫码登录与公开可访问的公众号/文章数据，不绕过验证码、登录限制、访问控制、频率限制或微信风控。
