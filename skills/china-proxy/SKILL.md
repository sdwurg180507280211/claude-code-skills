---
name: china-proxy
description: Detect and apply a local proxy for command-line tools when GitHub, PyPI, npm, Docker Hub, or other international services are failing to connect, or when the user explicitly asks for proxy setup in mainland China. Use for network/proxy troubleshooting, not for every ordinary mention of GitHub or an international service.
---

# China Proxy Manager

Use this skill when a command-line network operation needs a local proxy, especially after a connection timeout/failure or when the user explicitly requests proxy configuration.

## Workflow

1. Detect whether a known local proxy port is listening:

```bash
python ~/.claude/skills/china-proxy/scripts/detect_proxy.py
```

2. If a proxy is available, apply it to the single command where possible:

```bash
https_proxy=http://127.0.0.1:7890 \
http_proxy=http://127.0.0.1:7890 \
git clone https://github.com/owner/repo.git
```

3. Retry the failed operation and report whether the proxy changed the result.

## Common tools

### Git / curl / wget / Python

Prefer temporary environment variables so the setting does not leak into unrelated sessions:

```bash
export https_proxy=http://127.0.0.1:7890
export http_proxy=http://127.0.0.1:7890
```

### npm

For a one-off shell session, environment variables are usually enough. Only write persistent npm proxy configuration when the user explicitly wants it.

## Guardrails

- Do not activate merely because a GitHub URL appears; use it for actual connectivity/proxy needs.
- Detect before applying a proxy.
- Prefer command-scoped or session-scoped proxy settings.
- Do not change global Git/npm configuration unless the user explicitly asks for persistent configuration.
- If no proxy is running, report that clearly instead of inventing one.
