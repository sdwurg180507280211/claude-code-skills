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
| [`content-research-writer`](skills/content-research-writer) | Utility | 上游 vendored：研究 → 大纲 → 引用 → 高质量文章；用于补足插件市场不可达的主 Writer |
| [`wechat-medical-writer`](skills/wechat-medical-writer) | Utility | 医学领域上下文/资料约束 → 强制 handoff 给 `content-research-writer` → 按需配图/排版/发布 |

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

`utility-skills` 会同时安装 `content-research-writer` 与 `wechat-medical-writer`，因此医学写作链路不会再因为主 Writer 不在外部市场而缺失。

### 手动安装单个 Skill

```bash
cp -R skills/<skill-name> ~/.claude/skills/
```

如果手动安装 `wechat-medical-writer`，同时复制 `skills/content-research-writer/`。

### 公众号下游（按需）

纯研究/写作不要求安装排版或发布 upstream。

常规文章需要配图、微信公众号 HTML 或上传草稿箱时安装苍何：

```text
/plugin marketplace add freestylefly/canghe-skills
/plugin install content-skills@canghe-skills
/plugin install utility-skills@canghe-skills
```

如果文章是专家访谈 / Q&A / 对话气泡 / 卡片 / timeline / hero 等复杂组件布局，可额外安装 `xiaohu-wechat-format` 作为高级 formatter：

```bash
cd ~/.claude/skills/
git clone https://github.com/xiaohuailabs/xiaohu-wechat-format.git
cp xiaohu-wechat-format/config.example.json xiaohu-wechat-format/config.json
pip3 install markdown requests
```

当前只使用它的排版能力；封面、配图和最终草稿箱发布仍优先走苍何，避免维护两套发布链。该 upstream 当前 README 声明 MIT，但仓库没有独立 `LICENSE` 文件，因此本仓库不 vendor 它。

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
│   ├── content-research-writer/
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
- `UPSTREAM.lock.json` 锁定的 vendored 文件是否发生未声明漂移
- `wechat-account-bookmarks` 的核心离线测试是否通过
- `wechat-android-shortcuts` 的 Python 脚本是否可编译、核心离线测试是否通过
- `wechat-ios-shortcuts` 的 Web Clip 生成器是否可编译、核心离线测试是否通过

## 维护原则

- 仓库只保留自己真正维护、会继续迭代的 Skill，或为解决明确安装缺口而保留的受控 vendored upstream。
- 大型通用上游 Skill 默认不复制；只有在实际安装不可达、许可证明确允许、且确实是当前链路必需时，才允许 vendor。vendored Skill 必须保留许可证、来源、固定版本与同步说明，并使用完整性锁防止无意魔改。
- `content-research-writer` 是当前唯一这一类例外：来源 `CommandCodeAI/agent-skills`，MIT License；医学特有逻辑不得写入其 `SKILL.md`。
- Skill 的触发描述应足够具体，避免“只要提到 GitHub 就触发”这类过宽规则。
- 不提交 Cookie、Token、二维码登录态、真实用户输入、运行输出或缓存。
- 医学资料包只用于定义内容方向或作为运行时参考，不提交用户上传的 ZIP/PPT/PDF、内部培训材料、患者资料或未公开研究资料。
- `wechat-medical-writer` 保持为薄编排层：通用写作阶段必须 handoff 给 `content-research-writer`；面向公开发布的关键医学事实默认要求可核验来源；常规排版使用苍何，访谈/Q&A 等复杂组件布局可按需调用外部 `xiaohu-wechat-format`；最终发布统一优先走 `canghe-post-to-wechat`。
- 微信浏览器书签、Android 真机自动化、iOS Web Clip 与医学内容编排保持为独立 Skill，通过文件/数据契约松耦合。

## License

根目录代码默认使用 [MIT License](LICENSE)。个别包含独立许可证的 Skill，以其目录内许可证为准；`content-research-writer` 保留其上游 MIT License 与版权声明。
