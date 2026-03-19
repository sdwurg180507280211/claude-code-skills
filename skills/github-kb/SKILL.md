---
name: github-kb
description: Manages local GitHub repository knowledge base. Triggers whenever user mentions "github", "repo", "repository", or "仓库". Searches local repos first, then GitHub. Handles repo downloads and maintains a registry. Use this skill for any GitHub-related queries, repository searches, or when user wants to clone/download repos.
---

# GitHub Knowledge Base Manager

This skill manages your local GitHub repository collection and helps you search both locally and on GitHub.

## Local Repository Directory

**Primary location**: `~/IdeaProjects` (configurable - adjust to your local projects directory)

> **Setup Note**: After installation, edit this file and change `~/IdeaProjects` to your actual local projects/repos directory path (e.g., `~/projects`, `~/code`, `~/repos`).

This directory contains your cloned GitHub repositories. A `CLAUDE.md` file in this directory maintains a registry of all repos with one-line summaries.

## Core Workflow

When the user mentions a repository, GitHub, or asks about code:

1. **Check local first**: Search the projects directory for matching repository names
2. **Read CLAUDE.md**: Check the registry for context about available repos
3. **Search locally**: If found locally, analyze the repo to answer the user's question
4. **Search GitHub**: If not found locally, use `gh` or `curl` to search GitHub
5. **Offer to clone**: If user wants a repo that's not local, offer to download it

## Directory Verification

At the start of each session using this skill, verify the directory exists:

```bash
ls ~/IdeaProjects
```

If the directory doesn't exist, ask the user for the correct path and remember it for this session.

## CLAUDE.md Registry

The file `~/IdeaProjects/CLAUDE.md` serves as a registry of all repositories. Format:

```markdown
# GitHub Repository Registry

- **repo-name**: One-line description of what this repo does
- **another-repo**: Brief summary
```

When you clone a new repo, update this file. When analyzing repos, read this file first for context.

## Cloning Repositories

When user asks to download/clone a repo:

1. Extract the repository name or URL
2. Clone to the directory: `git clone <url> ~/IdeaProjects/<repo-name>`
3. After successful clone, update CLAUDE.md with a one-line summary
4. Confirm completion to user

## Searching GitHub

Use these methods in order of preference:

**Method 1 - gh CLI** (if available):
```bash
gh repo search <query>
gh issue list --repo <owner/repo>
gh pr list --repo <owner/repo>
```

**Method 2 - curl** (fallback):
```bash
curl -s "https://api.github.com/search/repositories?q=<query>"
curl -s "https://api.github.com/repos/<owner>/<repo>"
```

## Answering User Questions

When user asks about a repo:
1. Check if it exists locally in the projects directory
2. If local, use Read/Grep/Glob tools to analyze and answer
3. If not local, search GitHub and offer to clone it
4. Provide concise, actionable answers
