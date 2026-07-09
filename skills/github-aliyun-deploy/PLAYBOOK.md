# 本地开发 → GitHub → 阿里云 ECS 自动部署 总纲 Playbook

> 适用：任何「本地写代码、push 到 GitHub、自动部署到阿里云 ECS 运行」的项目。
> 你看完这一份，把里面的 `{{占位符}}` 换成你的项目信息，就能把**任意一个项目**配成这条路。
> 原理：GitHub 自托管 Runner 主动连 GitHub 拉代码执行部署，**不需要 GitHub 反向 SSH 进服务器**，所以 22 端口可以长期关闭，天然安全。

---

## 0. 架构（一张图看懂）

```
[你的电脑 / 手机 Codex]                 [阿里云 ECS]
  改代码 → git push main   ──https──▶  GitHub.com
                                        │ 触发 Actions
                                        ▼
                                  self-hosted Runner（ECS 上常驻）
                                        │ checkout + docker compose up --build
                                        ▼
                                  Docker 容器 :8080（只绑 127.0.0.1）
                                        ▲
                                  宿主机 nginx 反代 80/443 ──▶ 公网访问
```

要点：**Runner 在服务器上、主动拉代码**，所以服务器只需要出网 + 暴露 80/443，22 端口可关。

---

## 1. 前置条件

| 项目 | 说明 |
|---|---|
| 阿里云 ECS | Ubuntu / Alibaba Cloud Linux / CentOS 均可，2C2G 起步 |
| 安全组 | 先临时放行 22 给你当前出口 IP（用完收紧）；80/443 对 `0.0.0.0/0` 开放 |
| GitHub 账号 | 装好 `gh` CLI（`brew install gh` 后 `gh auth login`），仓库公开或私有均可 |
| 域名（可选） | HTTPS 需要；没有也能先跑通 HTTP（用 IP 访问） |

---

## 2. 第一步：把项目容器化（本地做）

### 2.1 `Dockerfile`（零依赖 Node 服务示例，按需替换）
```dockerfile
FROM node:20-alpine
WORKDIR /app
ENV NODE_ENV=production
ENV PORT=8080
COPY package.json server.js ./
COPY public ./public
COPY data/.gitkeep ./data/.gitkeep
RUN addgroup -S app && adduser -S app -G app && chown -R app:app /app
USER app
EXPOSE 8080
CMD ["node", "server.js"]
```

### 2.1b Python 后端示例（FastAPI + uvicorn，注意 PyPI 镜像源）
```dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt .
# 踩坑：ECS 直连 PyPI 极慢/卡死，必须走阿里云镜像源（Node 项目无此坑）
RUN pip install -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com
COPY . .
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

> 多语言项目可拆成「后端容器 + 前端容器」两个服务：前端用 `node:20` 构建静态产物，再用 `nginx:alpine` 起一个反代容器，把 `/api` 转发到 `backend:8000`，对外只暴露前端容器端口。

### 2.2 `docker-compose.yml`（服务名/容器端口**不要随便改**，否则自动部署断）
```yaml
services:
  {{PROJECT}}:
    build:
      context: .
    image: {{PROJECT}}:latest
    container_name: {{PROJECT}}
    restart: unless-stopped
    environment:
      NODE_ENV: production
      PORT: 8080
      ADMIN_TOKEN: ${ADMIN_TOKEN:-replace-with-a-strong-token}
    ports:
      - "${BIND_ADDR:-127.0.0.1:8080}:8080"   # 只绑内网，由 nginx 反代
    volumes:
      - ./data:/app/data
```

### 2.3 `.dockerignore`（别把 .env / 数据 / 构建产物打进镜像）
```
node_modules
dist
.git
.github
docs
scripts
*.log
.env
.env.*
data/*
!.gitkeep
.DS_Store
```

### 2.4 `.env.example`（**只放示例，真实值绝不进仓库**）
```
NODE_ENV=production
ADMIN_TOKEN=__换成强随机值，例 openssl rand -hex 32__
BIND_ADDR=127.0.0.1:8080
```

> 健康检查的约定：服务里加一个 `GET /api/health` 返回 200，后面 Actions 用它做部署后自检。

### 2.5 多容器与端口规划（避开冲突）
- 当 `ports` **直接等于一个变量**（如 `ports: ["${BIND_ADDR}"]`，不拼接容器端口）时，`BIND_ADDR` 必须写全三段：`宿主机IP:宿主机端口:容器端口`，例如 `0.0.0.0:8090:8081`。只写 `0.0.0.0:8090` 会报 `invalid hostPort`。
  - 若用拼接写法 `"${BIND_ADDR:-127.0.0.1:8080}:8080"`，则 `BIND_ADDR` 只填 `127.0.0.1:8080` 这种「宿主IP:宿主端口」即可。
- **一台 ECS 跑多个项目时，宿主机发布端口要错开**：例如 sunyun-portal 已占 `80/443/8080`，新项目就用 `8090`（避开 8080/80），前端 nginx 容器内部仍可用 `8081`。
- 安全组只需对新端口（如 `8090`）单独加一条入方向 TCP 规则，公网才能访问。

---

## 3. 第二步：GitHub 仓库 + Actions 工作流

### 3.1 建仓库并推送
```bash
gh repo create {{OWNER}}/{{PROJECT}} --public --source=. --remote=origin --push
# 私有：把 --public 换成 --private
```

### 3.2 `.github/workflows/deploy.yml`
```yaml
name: Deploy to Aliyun ECS

on:
  push:
    branches: [main]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: self-hosted        # 关键：用服务器上的自托管 Runner
    steps:
      - uses: actions/checkout@v4
      - name: Deploy with Docker Compose
        run: |
          set -euo pipefail
          docker compose --env-file /opt/{{PROJECT}}/.env down || true
          docker compose --env-file /opt/{{PROJECT}}/.env up -d --build
          docker image prune -f
      - name: Health check
        run: |
          sleep 3
          curl -fsS http://127.0.0.1:8080/api/health || exit 1
```

> 注意 `runs-on: self-hosted` —— 没有这个，任务会永远排队等不到机器。

---

## 4. 第三步：阿里云 ECS 一次性初始化（只在服务器上做这一次）

### 4.1 登录 & 建部署用户
```bash
# 临时放开安全组 22 给你的当前出口 IP，操作完务必收紧
adduser deployer
usermod -aG sudo deployer 2>/dev/null || usermod -aG wheel deployer
```

### 4.2 装 Docker（含 compose 插件）
Ubuntu / Debian：
```bash
apt update && apt install -y git docker.io docker-compose-plugin
systemctl enable --now docker
usermod -aG docker deployer
```
Alibaba Cloud Linux / CentOS / Rocky（用阿里云 docker-ce 源，规避 compose 插件缺失）：
```bash
yum install -y yum-utils
yum-config-manager --add-repo https://mirrors.aliyun.com/docker-ce/linux/centos/docker-ce.repo
yum install -y git docker-ce docker-ce-cli containerd.io docker-compose-plugin
systemctl enable --now docker
usermod -aG docker deployer
```

> **踩坑 1：Docker 起不来（socket activation）**
> `systemctl enable --now docker.socket` 再 `systemctl restart docker`。
>
> **踩坑 2：直连 docker.io 拉镜像超时**
> 配镜像加速器（`/etc/docker/daemon.json`）：
> ```json
> { "registry-mirrors": [
>   "https://docker.m.daocloud.io",
>   "https://hub-mirror.c.163.com",
>   "https://mirror.baidubce.com"
> ] }
> ```
> 改完 `systemctl restart docker`。

> **踩坑 4：Python 项目 `pip install` 在 ECS 直连 PyPI 卡死（7 分钟无进展，CPU 仅 4 秒）**
> Node 项目用 npm 走的是 registry 或已配镜像，从没踩过；但 `pip` 默认直连 pypi.org 在 ECS 上极慢。
> 解决：`Dockerfile` 的 `pip install` 加阿里云源：`-i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com`（见 2.1b）。

> **踩坑 5：`BIND_ADDR` 缺容器端口 → compose 报 `invalid hostPort`**
> 当 `docker-compose.yml` 的 `ports` 直接等于变量（`ports: ["${BIND_ADDR}"]`，不拼容器端口）时，变量必须写全三段 `宿主机IP:宿主机端口:容器端口`，如 `0.0.0.0:8090:8081`。
> 只写 `0.0.0.0:8090` 会报 `invalid hostPort: "0.0.0.0:8090"`。
> 多项目共用 ECS 时，宿主机端口要错开（见 2.5），安全组也要对新端口单独放行。

### 4.3 项目目录 + 真实 .env（凭据只放这里）
```bash
mkdir -p /opt/{{PROJECT}} && chown -R deployer:deployer /opt/{{PROJECT}}
cat > /opt/{{PROJECT}}/.env <<'EOF'
NODE_ENV=production
ADMIN_TOKEN=__强随机值__
BIND_ADDR=127.0.0.1:8080
EOF
chown deployer:deployer /opt/{{PROJECT}}/.env && chmod 600 /opt/{{PROJECT}}/.env
```

### 4.4 注册 GitHub 自托管 Runner（整个方案的核心）
1. 仓库 `Settings → Actions → Runners → New self-hosted runner → Linux x64`。
2. 复制 GitHub 给出的安装命令，在 ECS 上以 `deployer` 执行：
```bash
su - deployer
# 直接在本机 curl 下载（推荐，避免大包传输截断）：
mkdir actions-runner && cd actions-runner
curl -o actions-runner.tar.gz -L <GitHub 给的下载链接>
tar xzf ./actions-runner.tar.gz
./config.sh --url https://github.com/{{OWNER}}/{{PROJECT}} --token <RUNNER_TOKEN>
sudo ./svc.sh install
sudo ./svc.sh start
```
> **踩坑 3：从本地 scp 传 Runner 包会截断（103MB/225MB）**
> 优先**在 ECS 上直接 curl 下载**；必须传的话用 `rsync -P --partial` 续传校验。
> **衍生坑：ECS 直连 GitHub releases 下载 Runner 包也可能被墙**（返回 "Not Found" 错误页而非包）。若服务器上已缓存**同版本** Runner 包（如另一项目目录下的 `actions-runner-linux-x64-<ver>.tar.gz`），直接 `cp` 复用即可，省去联网下载。

验证：GitHub 仓库 Runners 页面该 Runner 显示 **Idle / Online**。

### 4.5 公网访问（nginx 反代 + 安全组）
- 安全组入方向：80/443 → `0.0.0.0/0`；22 → 仅你的可信 IP（用完删）。
- 宿主机装 nginx，反代 `127.0.0.1:8080`：
```nginx
server {
    listen 80;
    server_name {{你的域名或_}};
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```
```bash
systemctl enable --now nginx
```

### 4.6 HTTPS（有域名再做，可选）
```bash
# 阿里云 ECS 用 snap 装 certbot 可能受限，用 pip 装更稳：
pip3 install certbot certbot-nginx || apt install -y certbot python3-certbot-nginx
certbot --nginx -d {{你的域名}}
# 证书每 90 天续期，加定时任务：0 3 * * * certbot renew --quiet
```
> 没有域名时先跑通 HTTP（用公网 IP 访问），域名到位再补 certbot。

---

## 5. 日常流程（手机也能全搞定）

1. 本地/手机改代码 → `git push origin main`（或手机 GitHub App 合并 PR）。
2. Runner 自动 `checkout → docker compose up -d --build → 健康检查`。
3. 浏览器访问公网域名/IP 即可看到更新。
4. 改了 `.env` 里的凭据？直接在 `/opt/{{PROJECT}}/.env` 改值，再 push 一次触发部署即可。

---

## 6. 给「手机端 AI（Codex / ChatGPT / 其他）」的重用提示词模板

把下面整段粘贴到手机端 AI（已连接本仓库），换掉 `{{具体任务}}`：
```
你正在维护 GitHub 仓库 {{PROJECT}}（{{公司/项目说明}}）。

## 项目现状（不要推翻，沿用）
- 技术栈：{{简述，如 纯静态前端 + Node.js 内置 HTTP 服务端，零第三方运行时依赖}}
- 已具备 Docker 部署：Dockerfile / docker-compose.yml / .github/workflows/deploy.yml（push 到 main 由 ECS 自托管 Runner 自动部署）。
- 表单/接口字段名（勿改，前端依赖）：{{列出关键字段与钩子 ID}}
- 设计风格：{{如 极简信任风，单一强调色 #0e7d6b}}

## 本次任务
{{具体任务}}

## 硬性约束
1. 密码/密钥/数据库凭据一律走环境变量，绝不写死进代码；本地只提交 .env.example。
2. 保持零/最少第三方依赖（构建部署脚本除外）。
3. 不要改动 docker-compose.yml 的服务名与容器端口 8080，否则自动部署会断。

## 交付要求
完成后创建 PR（目标 main），描述写清：改了什么、如何本地验证、如何部署（合并即自动部署）、如何访问（公网地址）。
```

---

## 7. 排错速查

| 现象 | 原因 | 解决 |
|---|---|---|
| Actions 任务一直排队 | `runs-on` 写错 / Runner 离线 | 确认 `self-hosted`；`su - deployer && sudo ./svc.sh status` |
| Docker 启动失败 | socket activation | `systemctl enable --now docker.socket` 后 `restart docker` |
| 拉镜像超时 | 国内直连 docker.io 慢 | 配 `registry-mirrors` 加速器后 `restart docker` |
| 部署后访问 502 | 容器没起 / 端口没绑对 | ECS 上 `docker compose --env-file /opt/{{PROJECT}}/.env logs` 看容器日志 |
| 健康检查失败 | 服务没暴露 `/api/health` | 在代码加该路由返回 200 |
| 想换凭据 | .env 改了没生效 | 直接在 `/opt/{{PROJECT}}/.env` 改值，再 push 一次触发重部署 |
| 构建阶段 pip 卡死 | ECS 直连 PyPI 超时 | Dockerfile `pip install` 加阿里云源 `-i https://mirrors.aliyun.com/pypi/simple/ --trusted-host mirrors.aliyun.com` |
| compose 报 `invalid hostPort` | BIND_ADDR 缺容器端口 | 变量写全三段 `0.0.0.0:宿主端口:容器端口`（如 `0.0.0.0:8090:8081`） |

---

## 8. 方法论（为什么这么走，能套到任何项目）

1. **主线单一，链路最短**：本地改 → push main → Runner 自动部署，中间没有手动 SSH 步骤。
2. **Runner 主动拉，服务器被动**：不开放入站 SSH，攻击面最小，关机也不影响（Runner 会重连）。
3. **凭据与代码分离**：`.env` 在服务器本地 + `chmod 600`，仓库只留 `.env.example`。
4. **容器化是通用底座**：任何语言的服务都能塞进 Docker，部署脚本不变。
5. **约定优于配置**：固定服务名、固定 8080、固定 `/api/health`，自动部署脚本才稳定。
6. **先跑通 HTTP 再上 HTTPS**：降低首次成功率门槛，证书是增量能力。
7. **把"踩坑"写进文档**：镜像加速器、socket 激活、Runner 包传输截断，都固化进本 Playbook，下次直接跳坑。

---

> 本文件配套 Skill：`github-aliyun-deploy`（已安装到用户级 skills，下次直接说"按那个部署套路配一下 XX 项目"即可调用）。
