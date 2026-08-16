---
name: github-kb
description: Maintain and search a local knowledge base of cloned GitHub repositories. Use when the user wants to search local repositories, reuse local source code, clone a repository into the local project collection, or maintain a local repo registry. Do not trigger for ordinary public GitHub questions that do not need the local repository collection.
---

# GitHub Local Knowledge Base

Use a local repository collection as the first source when the task is specifically about the user's cloned projects or reusable local code.

## Repository root

Prefer an explicit project root supplied by the user. Otherwise use `GITHUB_KB_ROOT` when set; if neither is available, use `~/projects` as a conventional default and confirm it exists before writing there.

## Workflow

1. Check the local repository root for an exact or likely repository match.
2. If a local repository exists, inspect it locally before searching remote GitHub.
3. If the requested repository is not local and the user wants a local copy, clone it into the repository root.
4. Maintain an optional `CLAUDE.md` registry in the repository root with one concise line per cloned repository.
5. Never overwrite an existing local repository silently.

## Local registry format

```markdown
# GitHub Repository Registry

- **repo-name**: One-line description
- **another-repo**: One-line description
```

## GitHub access

Use the environment's native GitHub connector/tool when available. Fall back to `gh` or the GitHub REST API only when appropriate for the runtime.

## Guardrails

- Do not trigger on every mention of “GitHub”, “repo”, or “repository”.
- Do not clone repositories unless a local copy is useful for the requested task.
- Do not assume `~/IdeaProjects` or another machine-specific path.
- Do not modify the user's local registry or clone location without a clear task reason.
