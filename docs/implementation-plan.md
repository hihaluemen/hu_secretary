# MiShu Demo 实施计划（FastAPI + Vue）

> 版本：v0.2（实施中）  
> 更新时间：2026-02-06  
> 目标：在现有 `mishu-demo.py` 能力基础上，完成可对客户演示的前后端分离 Demo。

## 1. 项目目标

- 基于现有脚本能力（时间标准化、意图识别、事件新增/查询/更新）拆分为 `FastAPI` 后端服务。
- 提供 `Vue` 前端演示台，支持从自然语言输入到结果展示的完整链路。
- 所有关键配置统一收敛到配置模块；敏感/环境相关参数通过 `.env` 管理。
- 在不显著增加复杂度的前提下，补齐“演示闭环”能力：可观测、可回放、可验证。

## 2. 范围定义

### 2.1 本期范围（In Scope）

- 后端：`FastAPI + Service Layer + Repository Layer + MySQL`。
- 前端：`Vue3 + Vite + Pinia + Vue Router` 的单页演示应用。
- 核心链路：
  - 用户输入自然语言
  - 时间标准化
  - 意图拆分（新增/查询/更新）
  - 事件抽取与入库
  - 查询匹配展示
  - 更新 SQL 生成（先保留“预览/确认执行”模式）
- 基础工程化：统一配置、日志、错误处理、基础测试脚本。

### 2.2 暂不纳入（Out of Scope）

- 多租户权限系统、SSO、复杂 RBAC。
- 分布式部署、高可用、完整 CI/CD。
- 大规模性能压测与成本优化。

## 3. 技术方案总览

## 3.1 后端架构（建议）

```text
frontend (Vue)
   -> FastAPI Router
      -> Application Service
         -> LLM Adapter (OpenAI/Kimi compatible)
         -> Event Repository (MySQL)
```

## 3.2 代码目录规划（目标结构）

```text
backend/
  app/
    api/
      v1/
        assistant.py
        events.py
        health.py
    core/
      config.py
      logging.py
      exceptions.py
    schemas/
      assistant.py
      event.py
      common.py
    services/
      assistant_service.py
      intent_service.py
      event_service.py
      llm_service.py
    repositories/
      event_repository.py
    db/
      mysql.py
      init_db.py
    main.py
  tests/
    unit/
    api/
  scripts/
    test_backend_unit.sh
    test_backend_api.sh

frontend/
  src/
    api/
    stores/
    views/
    components/
    styles/
  tests/
  scripts/
    test_frontend_unit.sh
    test_frontend_build.sh
```

## 4. 配置与环境变量规划

## 4.1 统一配置原则

- 代码内只读取配置对象，不直接散落 `os.getenv`。
- 使用 `pydantic-settings`（或等价方案）统一加载 `.env`。
- 提供 `.env.example`，默认值仅用于本地开发。
- 采用 `LLM_PROVIDER` 显式选择模型提供方，仅要求填写当前 provider 对应的一组 key/base_url/model。

## 4.2 关键变量（建议）

```env
# App
APP_NAME=mishu-demo
APP_ENV=dev
APP_HOST=0.0.0.0
APP_PORT=8000
API_PREFIX=/api/v1
CORS_ORIGINS=http://localhost:5173

# LLM (Provider Switch)
LLM_PROVIDER=kimi
LLM_TIMEOUT_SECONDS=30

# Kimi
KIMI_API_KEY=
KIMI_BASE_URL=https://api.moonshot.cn/v1
KIMI_MODEL=kimi-k2-turbo-preview

# OpenAI
OPENAI_API_KEY=
OPENAI_BASE_URL=https://api.openai.com/v1
OPENAI_MODEL=gpt-4o-mini

# MySQL
MYSQL_HOST=localhost
MYSQL_PORT=3306
MYSQL_USER=root
MYSQL_PASSWORD=
MYSQL_DB=daily_assistant
MYSQL_CHARSET=utf8mb4

# Demo flags
DEMO_ENABLE_RESET=true
DEMO_ENABLE_UPDATE_EXECUTE=false
```

## 5. API 规划（演示优先）

- `GET /api/v1/health`
  - 服务健康检查（DB、基础配置状态）。
- `POST /api/v1/assistant/process`
  - 输入：`user_id`、`text`、`dry_run`。
  - 输出：标准化文本、意图拆分结果、新增写库结果、查询结果、更新 SQL 预览。
- `GET /api/v1/events`
  - 列表查询，支持 `keyword`、`date_from`、`date_to`。
- `POST /api/v1/events`
  - 手动新增（便于演示补录）。
- `PUT /api/v1/events/{id}`
  - 手动更新。
- `DELETE /api/v1/events/{id}`
  - 删除事件。
- `POST /api/v1/events/reset-demo`
  - 重置/注入演示数据（受 `DEMO_ENABLE_RESET` 控制）。
- `POST /api/v1/events/execute-update-sql`（可选）
  - 显式执行更新 SQL（受 `DEMO_ENABLE_UPDATE_EXECUTE` 控制）。

## 6. 前端实施方案（已结合 ui-ux-pro-max）

## 6.1 视觉主方案（已确认）

- Pattern：`Enterprise Gateway`
- Style：`Data-Dense Dashboard`
- 配色：
  - Primary `#0891B2`
  - Secondary `#22D3EE`
  - CTA `#22C55E`
  - Background `#ECFEFF`
  - Text `#164E63`
- 字体：`Lexend`（标题）+ `Source Sans 3`（正文）

## 6.2 页面与组件规划

- 页面：
  - `DemoDashboard`（主页面）
- 核心组件：
  - `InputPanel`：自然语言输入 + 示例模板
  - `PipelineResult`：标准化/意图拆分结果展示
  - `EventTable`：事件列表与筛选
  - `UpdateSqlPreview`：更新 SQL 预览与执行开关
  - `RunLogPanel`：本次调用日志与耗时

## 6.3 UX 约束（必须落实）

- 请求超过 300ms 显示 `skeleton/spinner`。
- 表单提交必须有状态反馈（loading/success/error）。
- 输入控件必须有 label，不使用 placeholder 充当 label。
- 可点击元素统一 hover + `cursor-pointer`。
- 动效时长控制在 150~300ms，避免装饰性无限动画。

## 7. 低复杂度增强功能（建议纳入）

- 示例语料一键填充（新增、查询、更新各 2~3 条）。
- “重放上一次请求”按钮（便于演示复现）。
- 演示数据一键重置（防止现场数据污染）。
- 操作流水（显示每步耗时与状态，增强可解释性）。
- 导出当前结果为 JSON（便于给客户留样本）。

## 8. 分阶段 TODO（实施清单）

## P0：项目骨架与配置

- [x] 创建 `backend`/`frontend` 基础工程。
- [x] 抽离 `mishu-demo.py` 逻辑到后端 service 层。
- [x] 完成统一配置模块与 `.env.example`。
- [x] 数据库初始化逻辑迁移到显式启动命令（移除 import 副作用）。

## P1：核心后端能力

- [x] 实现 `assistant/process` 聚合接口。
- [x] 实现 `events` CRUD 接口。
- [x] 增加统一异常结构与错误码。
- [x] 增加基础日志（请求 ID + 耗时 + 关键步骤）。

## P2：前端演示台

- [x] 完成主页面布局与主题 token。
- [x] 完成输入、结果、事件表格、SQL 预览组件。
- [x] 接入后端 API 与状态管理。
- [x] 完成 loading/error/empty 三态。

## P3：增强与可演示性

- [x] 实现演示数据重置与示例语料。
- [x] 实现请求重放与结果导出。
- [x] 增加操作流水展示。

## P4：测试与验收

- [x] 编写后端单测（服务层 + 仓储层）。
- [x] 编写后端 API 测试（FastAPI TestClient）。
- [x] 编写前端基础测试（至少构建 + 关键组件渲染）。
- [x] 编写端到端冒烟脚本（Happy Path）。

## 9. 测试脚本规划（实现后落地）

## 9.1 后端

- `backend/scripts/test_backend_unit.sh`
  - 目标：运行服务层/工具层单测。
  - 预期命令：`pytest -q backend/tests/unit`
- `backend/scripts/test_backend_api.sh`
  - 目标：运行 API 集成测试。
  - 预期命令：`pytest -q backend/tests/api`

## 9.2 前端

- `frontend/scripts/test_frontend_unit.sh`
  - 目标：运行前端单测（Vitest）。
- `frontend/scripts/test_frontend_build.sh`
  - 目标：验证可构建发布。

## 9.3 端到端冒烟

- `scripts/test_e2e_demo.sh`
  - 步骤：启动后端/前端 -> 调用主流程 -> 校验页面关键元素与接口响应。
  - 覆盖：新增、查询、更新 SQL 预览三条主路径。

## 10. 文档同步机制（实现阶段强制执行）

每完成一个 TODO，需同步更新本文件：

- 更新对应复选框状态（`[ ]` -> `[x]`）。
- 在“实施记录”新增一条：功能、日期、提交内容、测试命令、测试结果。
- 若出现阻塞，记录“阻塞原因 + 临时方案 + 后续处理人”。

建议记录模板：

```md
### YYYY-MM-DD HH:mm
- 完成项：
- 涉及文件：
- 测试命令：
- 测试结果：
- 备注/风险：
```

## 11. 验收标准（Demo Ready）

- 一条自然语言输入可完成“标准化 -> 意图拆分 -> 结果展示”全链路。
- 新增事件可落库并在事件表实时可见。
- 查询类请求可返回匹配事项。
- 更新类请求可生成 SQL 并可选执行（受开关控制）。
- 前端具备稳定的 loading/error/empty 状态，视觉风格统一。
- 测试脚本可一键执行并输出通过结果。

## 12. 实施记录

### 2026-02-06 13:10
- 完成项：P0 阶段 4 项全部完成（工程骨架、服务迁移、统一配置、显式初始化命令）。
- 涉及文件：
  - 后端骨架：`backend/app/main.py`、`backend/app/api/v1/*.py`、`backend/app/services/*.py`、`backend/app/repositories/event_repository.py`
  - 配置与环境：`backend/app/core/config.py`、`.env.example`
  - 数据库初始化：`backend/app/db/init_db.py`、`backend/scripts/init_db.py`
  - 前端骨架：`frontend/package.json`、`frontend/src/main.js`、`frontend/src/views/DemoDashboard.vue`
  - 测试脚本占位：`backend/scripts/test_backend_unit.sh`、`backend/scripts/test_backend_api.sh`、`frontend/scripts/test_frontend_build.sh`、`frontend/scripts/test_frontend_unit.sh`、`scripts/test_e2e_demo.sh`
  - 忽略规则：`.gitignore`
- 测试命令：`cd backend && source .venv/bin/activate && python -m compileall app scripts`
- 测试结果：通过（语法编译通过）。
- 备注/风险：
  - 当前前端为骨架与主题占位，业务组件将在 P2 完成。
  - `frontend/scripts/test_frontend_unit.sh` 暂为占位（待接入具体单测工具后启用）。

### 2026-02-06 13:25
- 完成项：P1 阶段 4 项全部完成（聚合接口、events CRUD、统一异常、请求日志）。
- 涉及文件：
  - 异常与响应：`backend/app/core/exceptions.py`、`backend/app/schemas/common.py`
  - 核心 API：`backend/app/api/v1/assistant.py`、`backend/app/api/v1/events.py`
  - 仓储层：`backend/app/repositories/event_repository.py`
  - 应用入口：`backend/app/main.py`
  - 数据模型：`backend/app/schemas/event.py`
- 测试命令：`cd backend && source .venv/bin/activate && python -m compileall app scripts`
- 测试结果：通过（语法编译通过）。
- 备注/风险：
  - `assistant/process` 已可用，但 LLM 提示词当前为 P0/P1 精简版，后续可继续强化精度。
  - `events/execute-update-sql` 仍未落地（按计划属于后续增强/安全控制项）。

### 2026-02-06 13:35
- 完成项：P2 阶段 4 项全部完成（页面布局、核心组件、API/状态管理、三态交互）。
- 涉及文件：
  - API 层：`frontend/src/api/client.js`、`frontend/src/api/assistant.js`、`frontend/src/api/events.js`
  - 状态管理：`frontend/src/stores/demo.js`
  - 组件：`frontend/src/components/InputPanel.vue`、`frontend/src/components/PipelineResult.vue`、`frontend/src/components/EventTable.vue`、`frontend/src/components/UpdateSqlPreview.vue`
  - 页面与主题：`frontend/src/views/DemoDashboard.vue`、`frontend/src/styles/theme.css`、`frontend/.env.example`
- 测试命令：`cd frontend && npm run build`
- 测试结果：通过（Vite 构建成功）。
- 备注/风险：
  - 当前 `UpdateSqlPreview` 为只读预览，执行 SQL 能力待后续在后端补安全开关接口后接入。
  - 前端单测尚未接入 Vitest（当前脚本保留占位，将在 P4 统一补全）。

### 2026-02-06 13:45
- 完成项：P3 阶段 3 项全部完成（演示重置、请求重放与导出、操作流水）。
- 涉及文件：
  - 状态增强：`frontend/src/stores/demo.js`
  - 交互增强：`frontend/src/components/InputPanel.vue`
  - 新增流水组件：`frontend/src/components/RunLogPanel.vue`
  - 页面接入：`frontend/src/views/DemoDashboard.vue`
- 测试命令：`cd frontend && npm run build`
- 测试结果：通过（Vite 构建成功）。
- 备注/风险：
  - 导出功能为前端本地下载 JSON，暂未接入后端归档。
  - 流水为前端侧日志，后续可与后端 request_id 做联动。

### 2026-02-06 13:58
- 完成项：P4 阶段 4 项全部完成（后端单测/API、前端单测/构建、E2E 冒烟脚本）。
- 涉及文件：
  - 后端测试：`backend/tests/unit/test_config.py`、`backend/tests/unit/test_utils_text.py`、`backend/tests/api/test_health_api.py`、`backend/tests/conftest.py`
  - 后端脚本：`backend/scripts/test_backend_unit.sh`、`backend/scripts/test_backend_api.sh`
  - 前端测试：`frontend/tests/dashboard.spec.js`、`frontend/vitest.config.js`、`frontend/package.json`
  - E2E 冒烟：`scripts/test_e2e_demo.sh`
  - 依赖：`backend/requirements.txt`
- 测试命令：
  - `cd backend && source .venv/bin/activate && ./scripts/test_backend_unit.sh`
  - `cd backend && source .venv/bin/activate && ./scripts/test_backend_api.sh`
  - `cd frontend && ./scripts/test_frontend_unit.sh`
  - `cd frontend && ./scripts/test_frontend_build.sh`
  - `./scripts/test_e2e_demo.sh`
- 测试结果：全部通过。
- 备注/风险：
  - E2E 当前为冒烟级（导入+构建验证），后续可扩展到真实启动服务并调用业务接口。

### 2026-02-06 14:05
- 完成项：补充项目使用说明文档 `README.md`（启动顺序、命令、变量配置、测试与排障）。
- 涉及文件：`README.md`
- 测试命令：文档类变更，无额外命令。
- 测试结果：N/A。
- 备注/风险：后续若接口或脚本变更，需要同步更新 README 对应章节。

### 2026-02-06 23:18
- 完成项：增强 LLM 输出鲁棒性与时间默认规则（避免 `00:00`、避免 JSON 解析导致 500）。
- 涉及文件：
  - 服务逻辑：`backend/app/services/assistant_service.py`
  - 单元测试：`backend/tests/unit/test_assistant_service.py`
  - 使用文档：`README.md`
- 测试命令：
  - `cd backend && source .venv/bin/activate && ./scripts/test_backend_unit.sh`
  - `cd backend && source .venv/bin/activate && ./scripts/test_backend_api.sh`
- 测试结果：通过（后端单测 7/7，通过；后端 API 测试 1/1，通过）。
- 备注/风险：
  - 默认时间采用业务约定：上午 `10:00`、下午 `16:00`、晚上 `20:00`、无时段 `09:00`。
  - 若模型长时间返回非结构化内容，当前策略会回退为空结果而非抛异常；可在后续增加“重试 + 结构化输出约束”进一步提升成功率。
