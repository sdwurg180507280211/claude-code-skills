---
name: chrome-devtools
description: Use Chrome DevTools MCP for browser-based testing and web page interaction. Trigger this skill whenever the user provides a URL, asks to visit/open/test a website, mentions checking a web page, wants to interact with browser elements, take screenshots, or perform any web testing tasks. Use this for URLs like https://example.com or when user says things like "访问这个网站", "打开这个页面", "测试这个链接", or provides any web address.
---

# Chrome DevTools Skill

Use the chrome-devtools MCP tools to interact with web pages for testing and automation.

## When to use this skill

Trigger when the user:
- Provides a URL (http://, https://)
- Asks to visit, open, access, or test a website
- Wants to interact with web page elements
- Needs screenshots or page snapshots
- Mentions browser testing or web automation
- Says "访问", "打开", "测试" with a URL or website context

## Check MCP availability

Before using chrome-devtools tools, verify the MCP is installed by checking available tools. If chrome-devtools MCP tools are not available, inform the user:

```
Chrome DevTools MCP 未安装。请运行以下命令安装：

claude mcp add chrome-devtools -- npx -y chrome-devtools-mcp@latest --autoConnect --channel=stable
```

## Using chrome-devtools

Once confirmed available, use the chrome-devtools MCP tools to:
- Navigate to URLs with `mcp__chrome-devtools__navigate_page` or `mcp__chrome-devtools__new_page`
- Take snapshots with `mcp__chrome-devtools__take_snapshot`
- Interact with elements using `mcp__chrome-devtools__click`, `mcp__chrome-devtools__fill`, etc.
- Capture screenshots with `mcp__chrome-devtools__take_screenshot`

Start by opening the page, then take a snapshot to understand the page structure before interacting with elements.
