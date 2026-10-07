# StudyFlow

> 面向个人开发者的学习与项目工作流管理系统

StudyFlow 是一个基于 **Python + FastAPI** 构建的个人学习与项目工作台，用于统一管理项目、任务、学习计划、Markdown 笔记和实际学习记录。

项目围绕：

```text
Project ── Task ── Study Plan
   │         └── Study Log
   └── Note
```

建立完整的个人工作流，并通过 Dashboard 对当前项目进度、任务状态和学习投入进行统一汇总。

当前版本为 **V1**，重点解决个人用户在项目开发和学习过程中“任务、计划、执行记录和知识沉淀相互分散”的问题。

---

## 项目概览

传统的 Todo List 通常只能回答：

> “还有哪些事情没有完成？”

StudyFlow 希望进一步回答：

> “我正在做什么项目？”

> “这个项目有哪些任务？”

> “接下来准备怎么做？”

> “实际投入了多少时间？”
> “过程中学到了什么？”

因此系统将项目执行和学习记录放在同一个数据模型中：

```text
                    ┌─────────────┐
                    │   Project   │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │    Task     │
                    └──────┬──────┘
                           │
             ┌─────────────┴─────────────┐
             ▼                           ▼
      ┌─────────────┐             ┌─────────────┐
      │    Plan     │             │ Study Log   │
      └─────────────┘             └─────────────┘

                    Project
                       │
                       ▼
                  ┌─────────┐
                  │  Note   │
                  └─────────┘
```

---

# 核心功能

## 1. 用户认证

提供完整的基础账户认证流程：

- 首次账户初始化
- 登录
- Logout
- 服务端 Session Cookie
- 密码哈希与验证
- 登录状态检查
- 受保护页面访问控制
- 用户数据隔离

首次使用：

```text
/setup
```

创建初始账户。

之后通过：

```text
/login
```

登录系统。

---

## 2. Projects

Projects 用于管理长期项目或学习主题。

支持：

- 创建项目
- 查看项目
- 编辑项目
- 归档项目
- 删除项目

项目是 StudyFlow 中最高层级的工作对象，可以进一步关联 Task 和 Note。

例如：

```text
StudyFlow
├── 后端开发
├── 数据库设计
├── 前端页面
└── 项目测试
```

---

## 3. Tasks

Task 是项目中的具体执行单元。

支持：

- 创建任务
- 查看任务
- 编辑任务
- 完成任务
- 删除任务
- 设置所属项目
- 设置优先级
- 设置截止日期

任务完成时记录：

```text
completed_at
```

重新打开任务时会清除对应完成时间。

因此任务不仅保存当前状态，也保留了完成状态对应的时间信息。

---

## 4. Study Plans

Study Plan 用于将任务进一步转化为具体的学习/工作安排。

支持：

- 创建学习计划
- 查看学习计划
- 编辑学习计划
- 删除学习计划
- 设置计划日期
- 设置预计学习分钟数
- 选择关联 Task

计划中的 Task 只能从当前登录用户拥有的任务中选择，避免跨用户访问数据。

---

## 5. Markdown Notes

Notes 用于保存项目开发和学习过程中产生的知识。

支持：

- 创建笔记
- 查看笔记
- 编辑笔记
- 删除笔记
- Markdown 内容
- Markdown 渲染
- 按标题搜索
- 关联当前用户自己的 Project

例如：

```markdown
# FastAPI 学习记录

## 今天完成

- 完成用户认证
- 完成 Task 管理
- 完成 Dashboard

## 遇到的问题

Uvicorn 使用了错误的 Python 环境。

## 解决方案

使用项目 `.venv` 中的 Python 启动服务。
```

---

## 6. Markdown 安全处理

StudyFlow 不直接将用户输入的 Markdown 原样输出为 HTML。

处理流程：

```text
用户输入 Markdown
        ↓
Markdown Parser
        ↓
生成 HTML
        ↓
nh3 清理
        ↓
安全 HTML
        ↓
浏览器
```

对生成的 HTML 进行安全清理，过滤潜在危险内容，例如：

- `<script>`
- HTML 事件属性
- 危险链接
- 其他不安全 HTML

这样可以在保留 Markdown 阅读体验的同时降低恶意 HTML 注入风险。

---

## 7. Study Logs

Study Log 用于记录实际投入的学习/工作时间。

支持：

- 创建学习记录
- 查看学习记录
- 编辑学习记录
- 删除学习记录
- 设置学习日期
- 设置实际学习分钟数
- 关联 Task

分钟数必须为正整数。

例如：

```text
2026-10-06
StudyFlow V1
实际学习时间：120 分钟
```

---

## 8. Dashboard

Dashboard 是整个系统的统一工作台。

当前 Dashboard 可以展示：

- Active Project 数量
- 未完成 Task 数量
- 最近任务
- 今日学习计划
- 今日计划预计学习分钟数
- 今日到期但未完成的任务
- 本周实际学习分钟数
- 累计实际学习分钟数
- 实际学习记录数量
- 已完成 Task 数量

同时区分：

```text
计划学习时间
      ↓
Study Plan

实际学习时间
      ↓
Study Log
```

两者不会混为一个统计值。

---

# 技术栈

| 技术 | 用途 |
|---|---|
| Python 3.12+ | 后端开发语言 |
| FastAPI | Web 应用框架 |
| Uvicorn | ASGI 开发服务器 |
| Jinja2 | 服务端 HTML 模板 |
| HTML / CSS | 页面结构与样式 |
| Native JavaScript | 页面交互 |
| SQLAlchemy 2.x | ORM |
| SQLite | 本地关系型数据库 |
| Alembic | 数据库 Schema 迁移 |
| Pydantic | 数据验证 |
| Markdown | Markdown 内容解析 |
| nh3 | HTML 安全清理 |
| pwdlib | 密码哈希接口 |
| Argon2 | 密码哈希算法 |

---

# 系统架构

StudyFlow V1 采用轻量级单体 Web 应用架构。

```text
┌───────────────────────────────────────┐
│                Browser                │
│                                       │
│          HTML / CSS / JS              │
└───────────────────┬───────────────────┘
                    │ HTTP
                    ▼
┌───────────────────────────────────────┐
│               FastAPI                 │
│                                       │
│  Auth    Dashboard    Projects        │
│  Tasks   Plans        Notes            │
│  Study Logs                           │
└───────────────────┬───────────────────┘
                    │
          ┌─────────┴─────────┐
          ▼                   ▼
┌──────────────────┐  ┌─────────────────┐
│ Application/Data │  │ Authentication  │
│      Layer       │  │   & Session     │
└─────────┬────────┘  └─────────────────┘
          │
          ▼
┌───────────────────────────────────────┐
│             SQLAlchemy                │
│                  ↓                    │
│               SQLite                  │
└───────────────────────────────────────┘
```

---

# 数据模型

当前系统主要包含：

```text
User
 │
 ├── Project
 │     │
 │     ├── Task
 │     │    │
 │     │    └── Study Plan
 │     │
 │     └── Note
 │
 └── AuthSession
```

同时：

```text
Task
 │
 └── Study Log
```

因此一个完整的学习/项目过程可以表示为：

```text
User
 ↓
Project
 ↓
Task
 ↓
Study Plan
 ↓
实际执行
 ↓
Study Log
 ↓
Note
```

---

# 用户数据隔离

StudyFlow V1 不仅检查用户是否登录，同时对业务数据进行用户级别的数据隔离。

核心原则：

```text
User A
 ├── Project A
 ├── Task A
 ├── Plan A
 ├── Note A
 └── Study Log A

User B
 ├── Project B
 ├── Task B
 ├── Plan B
 ├── Note B
 └── Study Log B
```

用户 A 不应该通过修改 URL 参数或表单数据访问用户 B 的业务数据。

因此项目、任务、学习计划、笔记和学习记录相关的查询与写入均基于当前登录用户进行约束。

这也是项目认证设计中除“登录”之外的重要部分：

```text
Authentication
      ↓
Who are you?

Authorization / Data Isolation
      ↓
What data are you allowed to access?
```

---

# 密码与 Session 安全

- 密码使用 Argon2 哈希后保存，不以明文存储。
- 登录状态由服务端 Session 记录维护；浏览器 Cookie 携带随机 Session token，数据库只保存该 token 的 SHA-256 哈希。
- Session Cookie 设置为 `HttpOnly` 和 `SameSite=Lax`；HTTPS 请求使用 `Secure` 属性。
- 业务数据查询和写入按当前用户进行隔离。
- 笔记 Markdown 先转换为 HTML，再由 `nh3` 清理允许的标签、属性和链接协议。
- 数据库结构由 Alembic migration 版本化管理。

## 公网部署前的安全加固

当前项目定位为**本地个人 V1**。如果未来部署到公网，应另外评估和配置：

- CSRF token；当前没有实现 CSRF token，`SameSite=Lax` 不等同于 token 防护。
- 首次账户创建期间对 `/setup` 入口进行限制，避免公开的新实例被他人抢先初始化。
- 登录尝试限制或 rate limiting。
- 全站 HTTPS，并确认反向代理正确传递 HTTPS 请求信息。
- 生产环境 secret 与配置的安全管理。

以上是公网部署前的评估事项，不代表这些措施已经在当前代码中实现。

---

# 数据库迁移

项目使用 Alembic 对数据库 Schema 进行版本管理。

当前 Migration：

```text
migrations/
└── versions/
    ├── 0001_create_users_and_auth_sessions.py
    ├── 0002_create_projects_and_tasks.py
    ├── 0003_create_study_plans.py
    ├── 0004_create_notes.py
    └── 0005_create_study_logs.py
```

数据库结构随着功能开发逐步演进：

```text
User / Auth
     ↓
Project / Task
     ↓
Study Plan
     ↓
Note
     ↓
Study Log
```

执行：

```powershell
alembic upgrade head
```

即可将数据库更新到最新 Schema。

---

# Dashboard 统计设计

Dashboard 的统计数据不单独建立冗余的 Statistics 表。

例如：

```text
今日学习时间
本周学习时间
累计学习时间
已完成 Task 数
Active Project 数
```

均基于现有：

```text
StudyLog
Task
Project
StudyPlan
```

实时计算。

这样做的主要考虑是避免：

```text
业务数据
   ↓
统计表
   ↓
统计数据
```

由于重复保存导致数据不一致。

实际采用：

```text
业务数据
   ↓
实时聚合
   ↓
Dashboard
```

从而保持统计结果与业务数据的一致性。

---

# 项目结构

```text
StudyFlow/
├── .env.example
├── .gitignore
├── README.md
├── alembic.ini
├── app/
│   ├── __init__.py
│   ├── auth.py
│   ├── database.py
│   ├── markdown_utils.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   │
│   ├── routers/
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── notes.py
│   │   ├── plans.py
│   │   ├── projects.py
│   │   ├── study_logs.py
│   │   └── tasks.py
│   │
│   ├── static/
│   │   └── css/
│   │       └── style.css
│   │
│   └── templates/
│       ├── dashboard.html
│       ├── index.html
│       ├── login.html
│       ├── note_detail.html
│       ├── note_form.html
│       ├── notes.html
│       ├── plan_form.html
│       ├── plans.html
│       ├── project_form.html
│       ├── projects.html
│       ├── study_log_form.html
│       ├── study_logs.html
│       ├── task_form.html
│       ├── tasks.html
│       └── setup.html
├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 0001_create_users_and_auth_sessions.py
│       ├── 0002_create_projects_and_tasks.py
│       ├── 0003_create_study_plans.py
│       ├── 0004_create_notes.py
│       └── 0005_create_study_logs.py
└── pyproject.toml
```

本地虚拟环境：

```text
.venv/
```

不纳入 Git。

`data/` 是运行时数据目录，不纳入 GitHub 仓库。应用的数据库初始化代码会在本地创建该目录；`data/studyflow.db` 是本地 SQLite 数据库文件，由 Alembic 迁移创建和维护数据库结构。数据库文件及 SQLite 临时伴随文件已加入 `.gitignore`。

`migrations/` 是数据库结构的版本控制来源。克隆仓库后执行 `alembic upgrade head`，即可在本地初始化数据库结构。

---

# 安装与运行

## 环境要求

- Windows
- Python 3.12（项目要求 Python >= 3.12，推荐使用 Python 3.12）
- PowerShell

---

## 创建虚拟环境

在项目根目录：

```powershell
py -3.12 -m venv .venv
```

激活：

```powershell
.\.venv\Scripts\Activate.ps1
```

如果 PowerShell 不允许执行激活脚本，也可以直接使用虚拟环境中的 Python。

---

## 安装依赖

```powershell
python -m pip install -e .
```

---

## 执行数据库迁移

首次运行：

```powershell
alembic upgrade head
```

该命令会执行当前所有 Alembic Migration，创建 SQLite 数据库结构。

---

## 启动开发服务器

```powershell
python -m uvicorn app.main:app --reload --port 8001
```

这里使用 `8001` 作为本地开发示例端口；如果该端口已被占用，可以换成其他可用端口。端口不是应用的固定要求。

首页：[http://127.0.0.1:8001](http://127.0.0.1:8001)

FastAPI 文档：[http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)

---

## 首次使用

打开 [http://127.0.0.1:8001/setup](http://127.0.0.1:8001/setup)：

创建初始账户。

然后访问 [http://127.0.0.1:8001/login](http://127.0.0.1:8001/login)：

登录。

登录成功后进入 [http://127.0.0.1:8001/dashboard](http://127.0.0.1:8001/dashboard)。

---

# 环境变量

项目提供：

```text
.env.example
```

如果需要使用环境变量：

```powershell
Copy-Item .env.example .env
```

然后启动：

```powershell
python -m uvicorn app.main:app --reload --port 8001 --env-file .env
```

---

# 页面与路由

## Authentication

```text
GET  /setup
POST /setup

GET  /login
POST /login

POST /logout
```

## Dashboard

```text
GET /dashboard
```

## Projects

```text
GET  /projects
GET  /projects/new
POST /projects
GET  /projects/{project_id}/edit
POST /projects/{project_id}/edit
POST /projects/{project_id}/archive
POST /projects/{project_id}/delete
```

## Tasks

```text
GET  /tasks
GET  /tasks/new
POST /tasks
GET  /tasks/{task_id}/edit
POST /tasks/{task_id}/edit
POST /tasks/{task_id}/complete
POST /tasks/{task_id}/delete
```

## Plans

```text
GET  /plans
GET  /plans/new
POST /plans
GET  /plans/{plan_id}/edit
POST /plans/{plan_id}/edit
POST /plans/{plan_id}/delete
```

## Notes

```text
GET  /notes
GET  /notes/new
POST /notes
GET  /notes/{note_id}
GET  /notes/{note_id}/edit
POST /notes/{note_id}/edit
POST /notes/{note_id}/delete
```

## Study Logs

```text
GET  /study-logs
GET  /study-logs/new
POST /study-logs
GET  /study-logs/{log_id}/edit
POST /study-logs/{log_id}/edit
POST /study-logs/{log_id}/delete
```

---

# FastAPI API Documentation

FastAPI 自动提供 API 文档。

启动项目后访问 [http://127.0.0.1:8001/docs](http://127.0.0.1:8001/docs)：

OpenAPI Schema：

[http://127.0.0.1:8001/openapi.json](http://127.0.0.1:8001/openapi.json)

Redoc：

[http://127.0.0.1:8001/redoc](http://127.0.0.1:8001/redoc)

---

# 当前开发进度

## Day 1 — 应用基础

已完成：

- FastAPI 基础项目
- Uvicorn 开发服务器
- 应用入口
- 首页
- Jinja2 HTML 模板
- 首页 CSS

---

## Day 2 — Authentication

已完成：

- SQLite
- SQLAlchemy ORM
- Alembic
- User Model
- AuthSession Model
- Argon2 密码哈希
- 首次账户初始化
- Login
- Logout
- Session Cookie
- Dashboard 认证保护
- 用户数据隔离基础

---

## Day 3 — Projects & Tasks

已完成：

- Project CRUD
- Project Archive
- Task CRUD
- Task Complete
- Task Priority
- Task Due Date
- Project / Task 关联
- Dashboard 基础统计
- Task `completed_at` 状态记录

---

## Day 4 — Study Plans

已完成：

- Study Plan CRUD
- 计划日期
- 预计学习分钟数
- Plan / Task 关联
- Dashboard 今日学习计划
- 今日预计学习分钟数
- 今日到期任务
- 当前用户数据隔离

---

## Day 5 — Markdown Notes

已完成：

- Note CRUD
- Markdown 内容
- Markdown 渲染
- HTML 安全清理
- 笔记标题搜索
- Note / Project 关联
- 页面导航

---

## Day 6 — Study Logs & Statistics

已完成：

- Study Log CRUD
- Study Log / Task 关联
- 学习日期
- 实际学习分钟数
- 今日学习时间
- 本周学习时间
- 累计学习时间
- 学习记录数量
- 已完成 Task 数量
- 计划时间与实际时间分离统计

---

---

# 工程设计重点

## 1. Authentication 与 Data Isolation 分离

项目不仅实现登录，还对每个业务对象进行当前用户约束。

重点数据包括：

```text
Project
Task
Study Plan
Note
Study Log
```

这意味着用户登录后仍然只能操作自己的业务数据。

---

## 2. 业务数据驱动 Dashboard

Dashboard 不维护独立统计数据，而是通过：

```text
Project
Task
StudyPlan
StudyLog
```

进行实时计算。

避免额外维护统计表带来的数据同步问题。

---

## 3. Database Migration

数据库结构通过 Alembic 版本化：

```text
0001
 ↓
0002
 ↓
0003
 ↓
0004
 ↓
0005
```

使数据库结构可以随着应用代码一起演进。

---

## 4. Markdown 安全处理

Markdown 并不是简单地：

```text
Markdown → HTML
```

而是：

```text
Markdown
   ↓
Parser
   ↓
HTML
   ↓
nh3 Sanitization
   ↓
Safe HTML
```

降低用户输入 HTML 带来的安全风险。

---

## 5. 轻量化技术选型

V1 没有引入：

- React
- Vue
- Redis
- Docker
- PostgreSQL
- 微服务
- 消息队列

而是采用：

```text
FastAPI
+
Jinja2
+
Native JavaScript
+
SQLAlchemy
+
SQLite
```

原因是当前项目定位为个人、本地、低维护成本系统。

技术选型围绕实际需求，而不是为了增加技术栈数量。

---

# 项目验证

V1 已完成本地应用验收。

主要验证内容包括：

- 应用正常启动
- 首页正常访问
- CSS 正常加载
- Setup 正常访问
- Login 正常访问
- 登录流程正常
- Dashboard 认证保护正常
- Projects 页面正常
- Tasks 页面正常
- Plans 页面正常
- Notes 页面正常
- Study Logs 页面正常
- OpenAPI 路由正常生成
- 用户业务数据隔离正常
- 数据库 Migration 正常工作

当前项目已经达到可以进行本地 V1 使用和项目展示的状态。

---

# 后续规划

后续功能按照“实际使用价值优先”的原则进行。

## V1.1

计划考虑：

- 更丰富的 Dashboard 可视化
- Task 筛选与排序
- 学习时间趋势
- 项目完成度统计
- 数据导出
- 数据备份
- 自动化测试完善

## V2

根据实际使用情况考虑：
- 全局搜索
- 标签系统
- 日历视图
- 文件附件
- 更完整的 API
- 多设备数据同步

以上功能目前均不属于 V1 已实现范围。

---

# 项目定位

StudyFlow 并不是一个单纯的 Todo List。

它更接近一个面向个人开发者的：

> **Project + Task + Planning + Learning Log + Knowledge Base 工作台**

核心工作流：

```text
                  ┌──────────┐
                  │ Project  │
                  └────┬─────┘
                       │
                       ▼
                  ┌──────────┐
                  │  Task    │
                  └────┬─────┘
                       │
              ┌────────┴────────┐
              ▼                 ▼
        ┌──────────┐      ┌──────────┐
        │   Plan   │      │ StudyLog │
        └──────────┘      └────┬─────┘
                               │
                               ▼
                         ┌──────────┐
                         │   Note   │
                         └────┬─────┘
                              │
                              ▼
                         ┌──────────┐
                         │Dashboard │
                         └──────────┘
```

最终形成：

```text
计划做什么
    ↓
实际做什么
    ↓
投入多少时间
    ↓
完成了什么
    ↓
学到了什么
    ↓
沉淀了什么
```

这也是 StudyFlow 与普通 Todo List 的主要区别。

---

# 项目总结

StudyFlow V1 通过一个轻量级 FastAPI Web 应用，将个人项目管理与学习记录结合起来。

项目覆盖了一个完整 Web 应用从基础到业务功能的主要组成部分：

```text
Python
  ↓
FastAPI
  ↓
Authentication
  ↓
Session
  ↓
SQLAlchemy
  ↓
SQLite
  ↓
Alembic
  ↓
Business Models
  ↓
Dashboard
  ↓
Markdown Processing
  ↓
Security
```

项目当前重点不在于功能数量，而在于建立一个完整、可运行、可维护的数据闭环。

---

## Tech Stack

```text
Python 3.12+
FastAPI
Uvicorn
Jinja2
SQLAlchemy 2.x
SQLite
Alembic
Pydantic
Markdown
nh3
pwdlib
Argon2
HTML
CSS
JavaScript
```

---

## Project Status

**V1 — Completed**

当前版本已经完成 Day 1 至 Day 6 的核心功能开发，并完成本地 V1 验收。

后续开发将以实际使用反馈为基础，而不是单纯增加功能数量。

---

## License

当前仓库暂未声明开源许可证。如需公开复用，应根据项目预期用途选择并添加适合的 LICENSE。
