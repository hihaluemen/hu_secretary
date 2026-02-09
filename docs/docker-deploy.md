# Docker 部署说明

本文档专门说明本项目的 Docker 部署参数与命令。

## 1. 相关文件

- `docker-compose.yml`：编排 `mysql` / `backend` / `frontend`
- `deploy.sh`：构建并启动
- `cleanup.sh`：停止并清理
- `logs.sh`：查看容器日志

## 2. 部署前准备

1) 安装 Docker（含 `docker compose`）

2) 准备环境变量文件：

```bash
cp .env.example .env
```

3) 按需填写 `.env` 里的 LLM 配置（`KIMI_API_KEY` 或 `OPENAI_API_KEY`）

## 3. 部署参数（`deploy.sh`）

### 3.1 常用参数

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `DOCKER_REGISTRY` | 空 | 镜像前缀，例如 `docker.1ms.run/` |
| `USE_CN_MIRROR` | `false` | 是否启用国内加速（pip/npm/apk） |
| `HTTP_PORT` | `8655` | 前端 HTTP 端口 |
| `HTTPS_PORT` | `8656` | 前端 HTTPS 端口 |
| `MYSQL_PORT` | `3306` | MySQL 映射端口 |
| `MYSQL_ROOT_PASSWORD` | 读取 `.env` 中 `MYSQL_PASSWORD` | 容器内 MySQL root 密码 |
| `MYSQL_DB` | 读取 `.env` 中 `MYSQL_DB` | 初始化数据库名 |

说明：

- `DOCKER_REGISTRY` 推荐带 `/` 结尾；不带也可以，`deploy.sh` 会自动补上。
- `USE_CN_MIRROR=true` 时：
  - 后端 `pip` 走清华源
  - 前端 `npm` 走 `npmmirror`
  - 前端运行镜像 `apk` 走阿里云镜像

### 3.2 登录镜像站参数（可选）

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `DOCKER_LOGIN` | `false` | 是否在 `deploy.sh` 内执行 `docker login` |
| `DOCKER_LOGIN_REGISTRY` | 空 | 登录的 registry 地址 |
| `DOCKER_LOGIN_USERNAME` | 空 | 登录用户名 |
| `DOCKER_LOGIN_PASSWORD` | 空 | 登录密码 |

## 4. 启动命令

### 4.1 你给出的启动方式（推荐）

```bash
DOCKER_REGISTRY=docker.1ms.run/ \
USE_CN_MIRROR=true \
HTTP_PORT=8655 \
HTTPS_PORT=8656 \
./deploy.sh
```

### 4.2 先手动 `docker login` 再启动

```bash
docker login docker.1ms.run -u 1ms -p '你的密码'

DOCKER_REGISTRY=docker.1ms.run/ USE_CN_MIRROR=true ./deploy.sh
```

更安全（避免密码进历史）：

```bash
echo '你的密码' | docker login docker.1ms.run -u 1ms --password-stdin
```

### 4.3 由脚本自动登录后启动

```bash
DOCKER_LOGIN=true \
DOCKER_LOGIN_REGISTRY=docker.1ms.run \
DOCKER_LOGIN_USERNAME=1ms \
DOCKER_LOGIN_PASSWORD='你的密码' \
DOCKER_REGISTRY=docker.1ms.run/ \
USE_CN_MIRROR=true \
./deploy.sh
```

## 5. 启动后检查

```bash
docker compose ps
docker compose logs -f backend
docker compose logs -f frontend
```

默认访问地址：

- 前端 HTTP：`http://localhost:8655`
- 前端 HTTPS：`https://localhost:8656`
- 后端健康检查（经前端反代）：`http://localhost:8655/api/v1/health`

## 6. 清理命令（`cleanup.sh`）

### 6.1 参数

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `REMOVE_IMAGES` | `false` | 是否删除本项目构建镜像 |
| `REMOVE_VOLUMES` | `false` | 是否删除数据卷（会清空 MySQL 数据） |

### 6.2 示例

仅停容器：

```bash
./cleanup.sh
```

停容器 + 删卷：

```bash
REMOVE_VOLUMES=true ./cleanup.sh
```

停容器 + 删镜像：

```bash
REMOVE_IMAGES=true ./cleanup.sh
```

全部清理：

```bash
REMOVE_IMAGES=true REMOVE_VOLUMES=true ./cleanup.sh
```

## 7. 日志查看（`logs.sh`）

### 7.1 参数

| 参数 | 默认值 | 说明 |
| --- | --- | --- |
| `SERVICE` | `all` | 服务名：`all` / `backend` / `frontend` / `mysql` |
| `FOLLOW` | `true` | 是否持续跟随日志 |
| `TAIL` | `200` | 默认展示最近多少行 |
| `SINCE` | 空 | 仅看某时间窗口，如 `10m` / `1h` |

### 7.2 示例

查看全部服务日志（默认跟随）：

```bash
./logs.sh
```

只看后端日志：

```bash
SERVICE=backend ./logs.sh
```

只看前端，且不跟随：

```bash
SERVICE=frontend FOLLOW=false ./logs.sh
```

看最近 500 行 MySQL 日志：

```bash
SERVICE=mysql TAIL=500 ./logs.sh
```

看后端最近 10 分钟日志：

```bash
SERVICE=backend SINCE=10m ./logs.sh
```
