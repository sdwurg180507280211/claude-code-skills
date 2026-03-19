# Claude Code Skills Collection

A curated collection of custom skills for [Claude Code](https://docs.anthropic.com/en/docs/claude-code), enhancing your development workflow with structured planning, browser testing, GitHub integration, and skill development tools.

## Skills Included

| Skill | Description |
|-------|-------------|
| **spec-mode** | Specification-driven development. Creates structured requirements, design docs, and task checklists before coding. |
| **chrome-devtools** | Browser-based testing via Chrome DevTools MCP. Navigate, interact, screenshot web pages. |
| **github-kb** | Local GitHub repository knowledge base. Search, clone, and manage repos with a registry. |
| **skill-creator** | Create, test, benchmark, and optimize custom Claude Code skills. |

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
├── chrome-devtools/    # Browser testing
│   └── SKILL.md
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
```

## Manual Installation

If you prefer not to use the install script:

```bash
# Copy individual skills
cp -r skills/spec-mode ~/.claude/skills/
cp -r skills/chrome-devtools ~/.claude/skills/
cp -r skills/github-kb ~/.claude/skills/
cp -r skills/skill-creator ~/.claude/skills/
```

## Post-Install Configuration

### github-kb
The `github-kb` skill defaults to `~/IdeaProjects` as the local repos directory. Edit `~/.claude/skills/github-kb/SKILL.md` and change the path to match your setup.

### chrome-devtools
Requires the Chrome DevTools MCP server. Install it with:
```bash
claude mcp add chrome-devtools -- npx -y chrome-devtools-mcp@latest --autoConnect --channel=stable
```

## Skill Usage

Skills trigger automatically based on context. You can also invoke them explicitly:

| Trigger | Skill |
|---------|-------|
| `/spec-mode` or mention "spec", "specification", "规范" | spec-mode |
| Provide a URL or ask to test a website | chrome-devtools |
| Mention "github", "repo", "repository", "仓库" | github-kb |
| Ask to create or improve a skill | skill-creator |

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
