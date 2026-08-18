# my-skills

个人维护的 Agent / Claude Code Skills 集合。仓库遵循“一个 Skill 一个目录、`SKILL.md` 为入口、脚本/参考资料/测试就近放置”的结构，尽量保持技能自包含、可验证、可独立安装。

## Skills

| Skill | 分类 | 用途 |
|---|---|---|
| [`spec-mode`](skills/spec-mode) | Development | 规格驱动开发：需求 → 设计 → 实现 |
| [`github-kb`](skills/github-kb) | Development | 本地 GitHub 仓库知识库与检索 |
| [`github-aliyun-deploy`](skills/github-aliyun-deploy) | Infrastructure | GitHub → 阿里云 ECS 自动部署 |
| [`china-proxy`](skills/china-proxy) | Infrastructure | 命令行访问受阻时探测并应用本地代理 |
| [`wechat-account-bookmarks`](skills/wechat-account-bookmarks) | Utility | 微信公众号 → Edge / Chrome 主页或文章书签 |
| [`wechat-android-shortcuts`](skills/wechat-android-shortcuts) | Utility | ADB 驱动微信官方“添加到桌面”，创建/检查 Android 公众号或小程序快捷方式 |
| [`wechat-ios-shortcuts`](skills/wechat-ios-shortcuts) | Utility | 名称 + URL → Apple Web Clip `.mobileconfig` → iPhone/iPad 主屏幕图标 |
| [`wechat-medical-writer`](skills/wechat-medical-writer) | Utility | 医学领域上下文/资料约束 → 复用成熟 Writer 完成文章 → 苍何配图/排版/发布 |

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
│   ├── spec-mode/
│   ├── wechat-account-bookmarks/
│   ├── wechat-android-shortcuts/
│   ├── wechat-ios-shortcuts/
│   └── wechat-medical-writer/
├── CHANGELOG.md
├── CLAUDE.md
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

每个 Skill 至少包含：

```text
skills/<skill-name>/
└── SKILL.md
```

按需要再增加 `scripts/`、`references/`、`examples/`、`tests/`、`templates/`、`README.md`。生成物、缓存、登录态、个人输入数据和私有医学资料不进入仓库。

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
- `wechat-android-shortcuts` 的 Python 脚本是否可编译、核心离线测试是否通过
- `wechat-ios-shortcuts` 的 Web Clip 生成器是否可编译、核心离线测试是否通过

## 维护原则

- 仓库只保留自己真正维护、会继续迭代的 Skill。
- 大型通用上游 Skill 不复制进来，优先直接使用上游版本，避免长期分叉。
- Skill 的触发描述应足够具体，避免“只要提到 GitHub 就触发”这类过宽规则。
- 不提交 Cookie、Token、二维码登录态、真实用户输入、运行输出或缓存。
- 医学资料包只用于定义内容方向或作为运行时参考，不提交用户上传的 ZIP/PPT/PDF、内部培训材料、患者资料或未公开研究资料。
- `wechat-medical-writer` 保持为薄编排层：主题到文章优先复用 `content-research-writer`，配图/排版/发布优先复用苍何 upstream，不在本仓库重复实现。
- 微信浏览器书签、Android 真机自动化、iOS Web Clip 与医学内容编排保持为独立 Skill，通过文件/数据契约松耦合。

## License

根目录代码默认使用 [MIT License](LICENSE)。个别包含独立许可证的 Skill，以其目录内许可证为准。
