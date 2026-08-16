# my-skills

个人维护的 Agent / Claude Code Skills 集合。仓库遵循“一个 Skill 一个目录、`SKILL.md` 为入口、脚本/参考资料/测试就近放置”的结构，尽量保持技能自包含、可验证、可独立安装。

## Skills

| Skill | 分类 | 用途 |
|---|---|---|
| [`spec-mode`](skills/spec-mode) | Development | 规格驱动开发：需求 → 设计 → 实现 |
| [`github-kb`](skills/github-kb) | Development | 本地 GitHub 仓库知识库与检索 |
| [`skill-creator`](skills/skill-creator) | Development | Skill 创建、评估与优化工具链 |
| [`github-aliyun-deploy`](skills/github-aliyun-deploy) | Infrastructure | GitHub → 阿里云 ECS 自动部署 |
| [`china-proxy`](skills/china-proxy) | Infrastructure | 国内开发环境代理探测与配置 |
| [`wechat-account-bookmarks`](skills/wechat-account-bookmarks) | Utility | 批量把微信公众号名称生成 Edge / Chrome 公众号主页书签 |

## 安装

### 推荐：Skills CLI

```bash
npx skills add sdwurg180507280211/my-skills
```

### Claude Code Plugin Marketplace

```text
/plugin marketplace add sdwurg180507280211/my-skills
```

然后按需安装：

```text
/plugin install development-skills@my-skills
/plugin install infrastructure-skills@my-skills
/plugin install utility-skills@my-skills
```

### 手动安装单个 Skill

```bash
cp -R skills/<skill-name> ~/.claude/skills/
```

## 仓库结构

```text
my-skills/
├── .claude-plugin/
│   └── marketplace.json
├── .github/
│   └── workflows/
│       └── validate-skills.yml
├── scripts/
│   └── validate_skills.py
├── skills/
│   ├── china-proxy/
│   ├── github-aliyun-deploy/
│   ├── github-kb/
│   ├── skill-creator/
│   ├── spec-mode/
│   └── wechat-account-bookmarks/
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

每个 Skill 至少包含：

```text
skills/<skill-name>/
└── SKILL.md
```

按需要再增加 `scripts/`、`references/`、`examples/`、`tests/`、`README.md`。生成物、缓存、登录态和个人输入数据不进入仓库。

## 校验

```bash
python3 scripts/validate_skills.py
```

仓库的 GitHub Actions 会在 push / pull request 时自动检查：

- 每个 Skill 是否存在 `SKILL.md`
- YAML frontmatter 是否包含 `name` / `description`
- `name` 是否与目录名一致
- 是否误提交缓存、虚拟环境、运行输出等文件
- Marketplace 是否只引用真实存在的 Skill
- `wechat-account-bookmarks` 的核心离线测试是否通过

## License

根目录代码默认使用 [MIT License](LICENSE)。个别包含独立许可证的 Skill，以其目录内许可证为准。
