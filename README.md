# Claude Code Skills Collection

A curated collection of custom skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code), enhancing your development workflow with structured planning, browser testing, GitHub integration, and skill development tools.

## Skills Included

### 🗺️ Skill Navigation

| Skill | Trigger Keywords | Use Case | Key Features |
|-------|-----------------|----------|--------------|
| **<a href="#spec-mode">spec-mode</a>** | `spec`, `规范`, `plan`, `design` | Complex feature development | Enforces requirements → design → implementation workflow, reduces rework |
| **<a href="#github-aliyun-deploy">github-aliyun-deploy</a>** | `阿里云`, `自动部署`, `deploy`, `runner`, `ECS` | 本地/手机改代码自动上线到阿里云 | push main → 自托管 Runner 自动 Docker 部署，22 端口可关 |
| **<a href="#github-kb">github-kb</a>** | `github`, `repo`, `clone`, `仓库` | Local repository knowledge base | Search local projects, maintain registry, auto-clone new repos |
| **<a href="#skill-creator">skill-creator</a>** | `create skill`, `improve skill`, `benchmark` | Skill development toolkit | Full lifecycle: create → test → evaluate → optimize with quantitative metrics |
| **<a href="#china-proxy">china-proxy</a>** | `proxy`, `代理`, `github`, `clone`, `下载`, `无法访问` | **China users essential** | Auto-detect and configure proxy for international network access |

---

## Skill Details

### <a id="spec-mode"></a> 📐 spec-mode - Specification-Driven Development

**When to use:** Complex features requiring planning, multi-file changes, architectural decisions.

**What it does:**
- Enforces 3-stage process: Requirements → Design → Implementation
- Creates structured documentation in `.kiro/specs/`
- Breaks work into tracked tasks with acceptance criteria

**Triggers on:** mention of "spec", "specification", "规范", or when planning complex features.

---

### <a id="github-kb"></a> 📚 github-kb - GitHub Repository Knowledge Base

**When to use:** Searching for code, cloning repos, answering questions about local projects.

**What it does:**
- Maintains a local registry of your repositories in `CLAUDE.md`
- Prioritizes local analysis over remote GitHub search
- Auto-clones requested repositories to your local disk

**Configurable:** Change the default projects path in `~/.claude/skills/github-kb/SKILL.md`.

---

### <a id="skill-creator"></a> 🔧 skill-creator - Skill Development Toolkit

**When to use:** Creating new Claude Code skills from scratch, optimizing existing ones.

**What it does:**
- Full development lifecycle with quantitative evaluation
- A/B testing and blind comparison of skill versions
- Automatic trigger description optimization
- HTML report viewer for evaluating results
- Apache 2.0 licensed - use freely in your own projects

**Most advanced skill** with ~2000 lines of Python tooling.

---

### <a id="china-proxy"></a> 🇨🇳 china-proxy - Auto Proxy Configuration for China Users

**When to use:** **CRITICAL - always required** for any international network operation.

**What it does:**
- Auto-detects running proxy on common ports (7890 → 7891 → 1087 → 8080)
- Configures environment variables for git, curl, wget, pip, npm
- Works with Clash, V2Ray, Shadowsocks, etc.
- No manual configuration needed

**Triggers on:** any GitHub URL, git clone, pip install, npm install, or mention of "proxy", "代理", "无法访问".

---

### <a id="github-aliyun-deploy"></a> ☁️ github-aliyun-deploy - 本地代码自动部署到阿里云 ECS

**When to use:** 想把本地/手机改完的代码自动发布到阿里云，无需手动 SSH 部署。

**What it does:**
- 一条闭环：push `main` → GitHub 自托管 Runner 自动 `docker compose up --build` 部署
- Runner 主动拉代码，服务器无需开放 22 端口（更安全）
- 含完整 Playbook（Docker 化、deploy.yml、ECS 初始化、nginx、certbot HTTPS 与踩坑）

**配套文档：** 见 `skills/github-aliyun-deploy/PLAYBOOK.md`。

## Quick Install

```bash
# Clone the repo
git clone https://github.com/<your-username>/claude-code-skills.git
cd claude-code-skills

# Install all skills
chmod +x install.sh
./install.sh

# Or install a specific skill
./install.sh spec-mode
```

## What Gets Installed

Skills are copied to `~/.claude/skills/`, which is the global skills directory for Claude Code. After installation, restart Claude Code or start a new session — skills are automatically discovered.

```
~/.claude/skills/
├── spec-mode/          # Structured spec development
│   └── SKILL.md
├── github-aliyun-deploy/  # GitHub → Aliyun ECS auto deploy
│   ├── SKILL.md
│   └── PLAYBOOK.md
├── github-kb/          # GitHub repo manager
│   ├── SKILL.md
│   └── evals/
├── skill-creator/      # Skill development toolkit
│   ├── SKILL.md
│   ├── agents/
│   ├── scripts/
│   ├── eval-viewer/
│   ├── assets/
│   └── references/
└── china-proxy/        # Auto proxy config for China users
    ├── SKILL.md
    └── scripts/
```

## Manual Installation

If you prefer not to use the install script:

```bash
# Copy individual skills
cp -r skills/spec-mode ~/.claude/skills/
cp -r skills/github-kb ~/.claude/skills/
cp -r skills/skill-creator ~/.claude/skills/
cp -r skills/github-aliyun-deploy ~/.claude/skills/
cp -r skills/china-proxy ~/.claude/skills/
```

## Post-Install Configuration

### github-kb
The `github-kb` skill defaults to `~/IdeaProjects` as the local repos directory. Edit `~/.claude/skills/github-kb/SKILL.md` and change the path to match your setup.

### github-aliyun-deploy
No special config. Follow `skills/github-aliyun-deploy/PLAYBOOK.md` to wire up your ECS and GitHub self-hosted Runner.

### china-proxy
No configuration needed! Automatically detects proxy on common ports (7890, 7891, 1087, 8080). Works with Clash, V2Ray, Shadowsocks, etc.

## Skill Usage

Skills trigger automatically based on context. You can also invoke them explicitly:

| Trigger | Skill |
|---------|-------|
| `/spec-mode` or mention "spec", "specification", "规范" | spec-mode |
| Say "自动部署到阿里云" / "把 XX 项目配成云端自动部署" | github-aliyun-deploy |
| Mention "github", "repo", "repository", "仓库" | github-kb |
| Ask to create or improve a skill | skill-creator |
| Mention "proxy", "代理", "翻墙", "无法访问" or when accessing international services | china-proxy |

## Uninstall

```bash
./install.sh --uninstall
```

## Contributing

1. Fork this repository
2. Add or modify skills in the `skills/` directory
3. Each skill must have a `SKILL.md` with YAML frontmatter (`name` and `description` required)
4. Submit a pull request

## License

- `skill-creator` is licensed under Apache 2.0 (see `skills/skill-creator/LICENSE.txt`)
- Other skills are provided as-is for personal use
