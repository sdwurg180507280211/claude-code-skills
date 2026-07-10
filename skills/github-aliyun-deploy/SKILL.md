---
name: github-aliyun-deploy
description: 把任意项目配成「本地/手机改代码 → push GitHub main → 阿里云 ECS 自托管 Runner 自动 Docker 部署」的闭环。当用户说"自动部署到阿里云""GitHub Actions 自托管 Runner""本地改代码自动上线""帮我把 XX 项目配成云端自动部署""手机 Codex 改完自动发布"时使用。涵盖 Docker 化、deploy.yml、ECS 初始化、nginx 反代、certbot HTTPS 与已知踩坑。
---

# 本地 → GitHub → 阿里云 ECS 自动部署

一套通用方法论：GitHub 自托管 Runner 在服务器上**主动拉代码**执行部署，不需要 GitHub 反向 SSH 进服务器，因此 22 端口可长期关闭。

## 何时用
- 用户要把某个本地项目做成「push 即部署」到阿里云。
- 用户有阿里云 ECS，希望手机/电脑改完代码自动上线。
- 用户已有一套这样的项目，想用相同套路套到另一个项目。

## 核心约定（自动部署稳定的前提）
- 服务名、容器端口（默认 8080）、健康检查路由 `/api/health` **固定不变**。
- 凭据只放服务器 `/opt/{{PROJECT}}/.env`（`chmod 600`），仓库只提交 `.env.example`。
- `runs-on: self-hosted` 才能用服务器上的 Runner。

## 执行流程（按需跳步，已存在的产物跳过）

### 1. 容器化（本地）
- `Dockerfile`：基础镜像按语言选，`USER` 非 root，`EXPOSE 8080`，`CMD` 启动服务。
  - **Node 轻量项目**（无原生编译依赖）：`node:20-alpine`。
  - **Node 含原生模块**（如 `better-sqlite3`、需 python/make/g++ 编译）：改用 `node:*-bookworm-slim`，`npm install` 走国内源 `registry.npmmirror.com`（见踩坑 C）。
  - **Python 后端**用 `python:3.13-slim` + `uvicorn` 起 `:8000`；`pip install` **务必加阿里云 PyPI 镜像源**（`-i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com`），否则 ECS 直连 PyPI 会卡死。
- `docker-compose.yml`：服务名 = `{{PROJECT}}`，`ports: "${BIND_ADDR:-127.0.0.1:8080}:8080"`（只绑内网，由 nginx 反代），`restart: unless-stopped`，挂载 `./data`。
- `.dockerignore`：排除 `node_modules dist .git .github docs scripts .env* data/* .DS_Store *.log`。
- `.env.example`：只放占位（如 `ADMIN_TOKEN=__强随机值__`）。

### 2. GitHub 仓库 + Actions
- `gh repo create {{OWNER}}/{{PROJECT}} --public --source=. --remote=origin --push`
- `.github/workflows/deploy.yml`（见下方模板）：on push main，job `runs-on: self-hosted`，步骤 checkout → `docker compose --env-file /opt/{{PROJECT}}/.env up -d --build` → 健康检查 `curl -fsS http://127.0.0.1:8080/api/health`。

### 3. 阿里云 ECS 一次性初始化（只在服务器做这一次）
- 临时放开安全组 22 给当前出口 IP，用完收紧。
- 建 `deployer` 用户并加入 `docker` 组。
- 装 Docker + compose 插件：
  - Ubuntu/Debian：`apt install -y git docker.io docker-compose-plugin`
  - Alibaba Cloud Linux/CentOS：先加阿里云 docker-ce 源再 `yum install -y docker-ce docker-compose-plugin`（避免 compose 插件缺失）。
- **踩坑 A — Docker 起不来（socket activation）**：`systemctl enable --now docker.socket` 再 `systemctl restart docker`。
- **踩坑 B — 拉镜像超时**：写 `/etc/docker/daemon.json` 配 `registry-mirrors`（daocloud / 163 / baidu），`systemctl restart docker`。
- **踩坑 C — 构建阶段卡死（npm / apt 在 ECS 直连慢）**：
  - **npm 重依赖项目**（如 Next.js）：`RUN npm install` 直连 `registry.npmjs.org` 在 ECS 上极慢（实测 8s/请求），几百个包基本跑不完。解决：Dockerfile 加 `--registry https://registry.npmmirror.com` + BuildKit 缓存挂载（`RUN --mount=type=cache,target=/root/.npm npm install --registry https://registry.npmmirror.com`）。
  - **Debian/Ubuntu 基础镜像 `apt-get update`**：Dockerfile 里若有 `apt-get install`（如给 `better-sqlite3` 装 `python3 make g++`），默认源 `deb.debian.org` 在 ECS 构建容器内常卡死。解决：先 `sed -i 's@deb.debian.org@mirrors.aliyun.com@g'` 再 `apt-get update`，并加 apt 缓存挂载。
  - **关键提醒：构建发生在 ECS 上，不是本地。** Runner 在服务器本地 `docker compose build`，所以**重应用首构建无缓存会跑 10–20 分钟，属正常、不是卡死**；中途不要 `docker buildx prune -f`，否则清空缓存强制全量重建，反而暴露网络问题。
- 建 `/opt/{{PROJECT}}/.env`（真实凭据，`chmod 600`）。
- **注册 Runner（核心）**：仓库 `Settings → Actions → Runners → New self-hosted runner → Linux x64`，复制命令在 ECS 以 `deployer` 执行。
  - **优先在 ECS 上直接 `curl` 下载 Runner 包**；必须本机传的话用 `rsync -P --partial`（scp 大包会截断）。
  - `./config.sh --url ... --token ...` → `sudo ./svc.sh install` → `sudo ./svc.sh start`。
  - 验证 GitHub Runners 页显示 **Idle / Online**。
- nginx 反代 `127.0.0.1:8080`（`listen 80`），`systemctl enable --now nginx`。安全组 80/443 对 `0.0.0.0/0` 开放。
- HTTPS（有域名再做）：`certbot --nginx -d {{域名}}`，定时 `certbot renew --quiet`。

### 4. 验证
- 本地/手机 push main → 看仓库 Actions 跑绿 → 公网访问域名/IP 看到更新。

## 复用模板

### deploy.yml
```yaml
name: Deploy to Aliyun ECS
on:
  push: { branches: [main] }
  workflow_dispatch:
jobs:
  deploy:
    runs-on: self-hosted
    steps:
      - uses: actions/checkout@v4
      - run: |
          set -euo pipefail
          docker compose --env-file /opt/{{PROJECT}}/.env down || true
          docker compose --env-file /opt/{{PROJECT}}/.env up -d --build
          docker image prune -f
      - run: |
          sleep 3
          curl -fsS http://127.0.0.1:8080/api/health || exit 1
```

### docker-compose.yml
```yaml
services:
  {{PROJECT}}:
    build: { context: . }
    image: {{PROJECT}}:latest
    container_name: {{PROJECT}}
    restart: unless-stopped
    environment:
      NODE_ENV: production
      PORT: 8080
      ADMIN_TOKEN: ${ADMIN_TOKEN:-replace-with-a-strong-token}
    ports:
      - "${BIND_ADDR:-127.0.0.1:8080}:8080"
    volumes:
      - ./data:/app/data
```

## 排错速查
| 现象 | 原因 | 解决 |
|---|---|---|
| 任务排队 | `runs-on` 错 / Runner 离线 | 确认 `self-hosted`；`su - deployer && sudo ./svc.sh status` |
| Docker 起不来 | socket activation | `enable --now docker.socket` 后 `restart docker` |
| 拉镜像超时 | 国内直连慢 | 配 `registry-mirrors` 后 `restart docker` |
| 502 | 容器未起/端口错 | `docker compose --env-file /opt/{{PROJECT}}/.env logs` |
| 健康检查失败 | 无 `/api/health` | 代码加该路由返回 200 |
| 换凭据 | .env 未生效 | 改 `/opt/{{PROJECT}}/.env` 再 push 触发重部署 |
| 构建阶段 npm 卡死 | ECS 直连 registry.npmjs.org 慢 | Dockerfile `npm install` 加 `--registry https://registry.npmmirror.com` + npm 缓存挂载（见踩坑 C） |
| 构建阶段 apt-get 卡死 | Debian 基础镜像直连 deb.debian.org | Dockerfile apt 步骤 `sed` 换 `mirrors.aliyun.com`（见踩坑 C） |
| 首次构建极慢（10+ 分钟） | 无缓存 + ECS 小机器 | 正常；构建在 ECS 本地跑，别中途 `docker buildx prune -f` |

## 给手机端 AI 的提示词模板
```
你正在维护 GitHub 仓库 {{PROJECT}}（{{说明}}）。
项目现状（沿用，勿推翻）：技术栈{{...}}；已具备 Docker 部署与 deploy.yml 自动部署；关键字段/钩子{{...}}；设计风格{{...}}。
本次任务：{{具体任务}}
硬性约束：1) 凭据走环境变量，不写死代码，只提交 .env.example；2) 保持最少依赖；3) 不改 docker-compose 服务名与 8080 端口。
交付：创建 PR（目标 main），写清改动、本地验证、部署方式、访问地址。
```

## 完整图文版
详见本目录 `PLAYBOOK.md`（所有占位符与踩坑细节都在那里）。
