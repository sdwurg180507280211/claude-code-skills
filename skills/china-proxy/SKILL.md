---
name: china-proxy
description: CRITICAL - Always use this skill when accessing GitHub, Google, PyPI, npm, or any international service. Automatically configures proxy (port 7890/7891/1087) for git clone, wget, curl, pip install, npm install. Triggers on ANY mention of GitHub URLs, international downloads, or when user says "代理", "翻墙", "proxy", "无法访问", "连接失败". This skill is REQUIRED for all international network operations to avoid connection failures.
---

# China Proxy Manager

IMPORTANT: This skill MUST be used for ALL operations accessing international services from China.

## Mandatory usage scenarios

You MUST use this skill when:
- ANY GitHub URL appears (github.com, githubusercontent.com, api.github.com)
- Running git clone, git push, git pull, git fetch
- Using wget or curl to download from international domains
- Installing packages: pip install, npm install, brew install
- Accessing: Google, PyPI, npmjs.org, Docker Hub, AWS, Azure
- User mentions: "代理", "翻墙", "proxy", "GitHub", "下载", "clone"

## Step-by-step workflow

**STEP 1**: Detect available proxy
```bash
python ~/.claude/skills/china-proxy/scripts/detect_proxy.py
```
This returns JSON like: `{"proxy": "http://127.0.0.1:7890", "available": true, "port": 7890}`

**STEP 2**: If proxy available, apply it to your command
```bash
export https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890
# Then run your command
```

**STEP 3**: Execute the command and document proxy usage in output summary

## Applying proxy by tool type

### Git commands
```bash
export https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890
git clone https://github.com/user/repo.git
```

Or configure git directly:
```bash
git config --global http.proxy http://127.0.0.1:7890
git config --global https.proxy http://127.0.0.1:7890
```

### Curl/Wget
```bash
export https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890
curl https://example.com
wget https://example.com/file.tar.gz
```

### Python requests
Set environment variables before running Python:
```bash
export https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890
python script.py
```

### Package managers
```bash
# pip
export https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890
pip install package

# npm
npm config set proxy http://127.0.0.1:7890
npm config set https-proxy http://127.0.0.1:7890
npm install package
```

## Workflow

1. When you see a command targeting international services, first run the proxy detection script
2. If proxy is available, prepend the command with proxy environment variables
3. Execute the command
4. If the command fails with connection errors, inform the user that proxy might not be running

## Examples

**Example 1: Download from GitHub**
```bash
# Step 1: Detect proxy
python ~/.claude/skills/china-proxy/scripts/detect_proxy.py
# Output: {"proxy": "http://127.0.0.1:7890", "available": true, "port": 7890}

# Step 2: Download with proxy
export https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890 && \
wget https://github.com/user/repo/releases/download/file.tar.gz
```

**Example 2: Git clone**
```bash
# Detect proxy first
python ~/.claude/skills/china-proxy/scripts/detect_proxy.py

# Clone with proxy
export https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890 && \
git clone https://github.com/user/repo.git
```

**Example 3: Curl API request**
```bash
export https_proxy=http://127.0.0.1:7890 http_proxy=http://127.0.0.1:7890 && \
curl https://api.github.com/repos/user/repo
```

## Important: Document proxy usage

When creating summary files, ALWAYS mention that proxy was used:
```
Download Summary
================
Proxy: http://127.0.0.1:7890 (detected and applied)
Source: https://github.com/...
Status: Success
```

## Important notes

- Always detect proxy availability before applying settings
- Use environment variables for one-off commands (preferred for temporary operations)
- Only modify global git config if user explicitly requests persistent settings
- After operations complete, you don't need to unset environment variables (they're scoped to the command)
- If proxy detection fails but user insists, try common ports in order: 7890, 7891, 1087
