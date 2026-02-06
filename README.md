# MiShu Demo（FastAPI + Vue）

一个可演示的「自然语言待办助手」Demo：

- 后端：`FastAPI` + `MySQL` + `LLM（Kimi/OpenAI 可切换）`
- 前端：`Vue3` + `Vite` + `Pinia`
- 功能链路：自然语言输入 -> 时间标准化 -> 意图拆分 -> 新增/查询 -> 更新 SQL 预览

---

## 1. 目录结构

```text
backend/   # FastAPI 后端
frontend/  # Vue 前端
scripts/   # E2E 冒烟脚本
docs/      # 实施计划与过程文档
```

---

## 2. 运行前准备

## 2.1 基础依赖

- Python 3.9+
- Node.js 18+
- MySQL 5.7+（或兼容版本）
- `uv`（用于 Python 依赖安装，按你的开发规范）

## 2.2 环境变量文件

在项目根目录创建：

```bash
cp .env.example .env
```

在前端目录创建：

```bash
cp frontend/.env.example frontend/.env
```

---

## 3. 必配环境变量说明

主配置文件：`.env`

## 3.1 应用基础

```env
APP_NAME=mishu-demo
APP_ENV=dev
APP_HOST=0.0.0.0
APP_PORT=8000
API_PREFIX=/api/v1
CORS_ORIGINS=http://localhost:5173
```

## 3.2 LLM 提供方（两套选一套）

通过 `LLM_PROVIDER` 选择：`kimi` 或 `openai`。

### A) 使用 Kimi

```env
LLM_PROVIDER=kimi
KIMI_API_KEY=你的_key
KIMI_BASE_URL=https://api.moonshot.cn/v1
KIMI_MODEL=kimi-k2-turbo-preview
LLM_TIMEOUT_SECONDS=30
```

### B) 使用 OpenAI

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=你的_key
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini
LLM_TIMEOUT_SECONDS=30
```

> 说明：不需要两套都填，按 `LLM_PROVIDER` 选择的那套配置完整即可。

## 3.3 MySQL

```env
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=你的密码
MYSQL_DB=daily_assistant
MYSQL_CHARSET=utf8mb4
```

## 3.4 Demo 开关

```env
DEMO_ENABLE_RESET=true
DEMO_ENABLE_UPDATE_EXECUTE=false
```

---

## 4. 启动顺序（很重要）

推荐顺序：

1. 启动/确认 MySQL
2. 启动后端（初始化数据库）
3. 启动前端
4. 打开页面演示

---

## 5. 后端启动

## 5.1 首次安装依赖

```bash
cd backend
source .venv/bin/activate
uv pip install -r requirements.txt
```

> 按你的规范：新增依赖时请使用 `uv pip install xxx`。

## 5.2 初始化数据库（建库建表）

```bash
cd backend
source .venv/bin/activate
python scripts/init_db.py
```

## 5.3 启动 FastAPI

```bash
cd backend
source .venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

后端地址：`http://localhost:8000`

健康检查：`http://localhost:8000/api/v1/health`

---

## 6. 前端启动

```bash
cd frontend
npm install
npm run dev
```

前端地址：`http://localhost:5173`

前端通过 `frontend/.env` 中的 `VITE_API_BASE_URL` 访问后端，默认值：

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_API_TIMEOUT_MS=120000
```

其中 `VITE_API_TIMEOUT_MS` 建议保持 `120000`（120 秒），避免 LLM 多轮处理时前端过早超时。

---

## 7. 演示建议流程

1. 进入前端页面，先点“示例：新增”，执行一次。
2. 查看“链路结果”和“事项列表”变化。
3. 点“示例：查询”，验证检索链路。
4. 点“示例：更新”，查看“更新 SQL 预览”。
5. 使用“重放上次 / 导出 JSON / 重置演示数据”展示完整闭环。

---

## 8. 后端 API 概览

- `GET /api/v1/health`
- `POST /api/v1/assistant/process`
- `GET /api/v1/events`
- `GET /api/v1/events/{event_id}`
- `POST /api/v1/events`
- `PUT /api/v1/events/{event_id}`
- `DELETE /api/v1/events/{event_id}`
- `POST /api/v1/events/reset-demo`

---

## 9. 测试命令

## 9.1 后端

```bash
cd backend
source .venv/bin/activate
./scripts/test_backend_unit.sh
./scripts/test_backend_api.sh
```

## 9.2 前端

```bash
cd frontend
./scripts/test_frontend_unit.sh
./scripts/test_frontend_build.sh
```

## 9.3 E2E 冒烟

```bash
./scripts/test_e2e_demo.sh
```

---

## 10. 常见问题

## Q1: `vitest: command not found`

前端依赖未安装完整：

```bash
cd frontend
npm install
```

## Q2: 后端连接 MySQL 失败

- 检查 MySQL 是否启动
- 检查 `.env` 中 `MYSQL_HOST/PORT/USER/PASSWORD`
- 重新执行 `python scripts/init_db.py`

## Q3: 前端调用后端报跨域

- 检查 `.env` 的 `CORS_ORIGINS` 是否包含 `http://localhost:5173`
- 检查前端 `VITE_API_BASE_URL` 是否指向正确后端地址
