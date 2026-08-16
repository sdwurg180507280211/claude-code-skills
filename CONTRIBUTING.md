# Contributing

## Skill 目录规范

- 使用小写 kebab-case 目录名，例如 `wechat-account-bookmarks`。
- 每个 Skill 必须包含 `SKILL.md`。
- `SKILL.md` 顶部必须有 YAML frontmatter：`name` 与 `description`。
- `name` 应与目录名完全一致。
- 运行脚本放 `scripts/`，长参考资料放 `references/`，样例放 `examples/`，离线测试放 `tests/`。
- Skill 尽量自包含；不要依赖个人电脑上的固定绝对路径。
- 不提交账号凭据、Cookie、Token、二维码登录态、个人输入数据、运行输出或缓存。
- 不为了“以后可能用到”增加额外兼容层；优先保持实现简单、可维护。

## 提交前检查

```bash
python3 scripts/validate_skills.py
```

如果 Skill 自带测试，也应先运行其测试。例如：

```bash
python3 -m unittest discover -s skills/wechat-account-bookmarks/tests -v
```
