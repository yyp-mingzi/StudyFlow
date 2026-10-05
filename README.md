# StudyFlow

StudyFlow 是一个个人学习与项目工作台，面向学生和个人开发者。目前已完成 Day 1 至 Day 6 的应用骨架、认证、项目任务、学习计划、Markdown 笔记、学习记录和学习统计功能。

## 环境要求

- Python 3.12 或更高版本

当前使用的主要技术：

- FastAPI 和 Uvicorn：后端应用与开发服务器
- Jinja2：HTML 页面模板
- Markdown 和 nh3：Markdown 解析与 HTML 安全清理
- SQLAlchemy 2.x 和 SQLite：ORM 与本地数据库
- Alembic：数据库迁移
- Pydantic：请求数据验证（由 FastAPI 使用）
- pwdlib 和 Argon2：密码哈希与验证

## 安装与启动（Windows PowerShell）

在项目根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
alembic upgrade head
python -m uvicorn app.main:app --reload
```

首次启动前运行 Alembic 迁移以创建 SQLite 数据库表。启动服务器后：

- 打开 <http://127.0.0.1:8000> 查看 StudyFlow 首页。
- 首次使用时打开 <http://127.0.0.1:8000/setup> 创建唯一的初始账户。
- 之后通过 <http://127.0.0.1:8000/login> 登录；登录成功后进入受保护的 Dashboard。
- Dashboard 可进入项目、任务、学习计划、笔记和学习记录页面，并提供退出登录按钮。

开发服务器启动后，修改文件会自动重新加载。SQLite 数据库文件位于 `data/studyflow.db`，由 Alembic 迁移创建，并已加入 Git 忽略规则。

如果 PowerShell 找不到可用的 `python` 命令，先将本机 Python 3.12 的安装目录加入 `PATH`；也可以把下面示例中的路径替换为本机的 `python.exe` 完整路径来创建虚拟环境：

```powershell
$PythonExe = 'C:\path\to\python.exe'
& $PythonExe -m venv .venv
```

如需使用示例环境变量，可先复制配置文件，再通过 Uvicorn 加载：

```powershell
Copy-Item .env.example .env
python -m uvicorn app.main:app --reload --env-file .env
```

## 当前状态

### Day 1 已完成

- FastAPI 基础项目和可启动的应用入口
- 使用 HTML 模板展示的 StudyFlow 首页
- 首页静态 CSS

### Day 2 已完成

- SQLite 数据库、SQLAlchemy ORM 和 Alembic 迁移
- `User` 与 `AuthSession` 数据模型
- 使用 Argon2 保存和验证密码哈希
- 首次账户初始化页面与流程
- 登录、服务端 Session Cookie 和 Logout
- 需要登录才能访问的 Dashboard
- 用户数据隔离：项目和任务查询限定为当前登录用户

### Day 3 已完成

- Projects：创建、查看、编辑、归档和删除
- Tasks：创建、查看、编辑、完成和删除，并支持所属项目、优先级和截止日期
- Dashboard 显示当前用户的 active 项目数、未完成任务数和最近任务
- Task 完成时记录 `completed_at`，重新打开时清除该时间

### Day 4 已完成

- Study Plans：创建、查看、编辑和删除学习计划，可设置日期、预计分钟数，并选择关联的当前用户任务
- Dashboard 显示今日学习计划和预计总分钟数、今日到期未完成任务、active 项目数、全部未完成任务数和最近任务
- Study Plan 和关联 Task 的读写均限定为当前登录用户

### Day 5 已完成

- Notes：创建、查看、编辑和删除 Markdown 笔记，可选择关联自己的项目
- 按标题搜索当前用户的笔记
- 渲染常见 Markdown 语法，并在输出前清理 HTML，过滤脚本、事件属性和危险链接
- Dashboard、Projects、Tasks、Plans、Notes 和 Study Logs 页面之间提供导航

### Day 6 已完成

- Study Logs：创建、查看、编辑和删除学习记录，可关联自己的 Task
- 学习记录按日期保存，分钟数必须为正整数
- Dashboard 根据当前用户数据计算今日、本周和累计实际学习分钟数及记录数、已完成 Task 数
- Dashboard 同时显示计划分钟数和实际记录分钟数，两者分别统计
- 统计由现有 StudyLog、Task 和 Project 数据实时计算，不单独保存统计表
- Dashboard、Projects、Tasks、Plans、Notes 和 Study Logs 页面之间提供导航

### 尚未实现

- AI Assistant

## 项目结构

```text
StudyFlow/
├── .env.example
├── .gitignore
├── .vscode/
│   └── settings.json
├── alembic.ini
├── app/
│   ├── __init__.py
│   ├── auth.py
│   ├── database.py
│   ├── markdown_utils.py
│   ├── main.py
│   ├── models.py
│   ├── schemas.py
│   ├── routers/
│   │   ├── auth.py
│   │   ├── dashboard.py
│   │   ├── notes.py
│   │   ├── plans.py
│   │   ├── projects.py
│   │   ├── study_logs.py
│   │   └── tasks.py
│   ├── static/
│   │   └── css/
│   │       └── style.css
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
├── data/
│   └── studyflow.db
├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       ├── 0001_create_users_and_auth_sessions.py
│       ├── 0002_create_projects_and_tasks.py
│       ├── 0003_create_study_plans.py
│       ├── 0004_create_notes.py
│       └── 0005_create_study_logs.py
├── pyproject.toml
└── README.md
```

`.venv/` 是本地虚拟环境目录，不纳入 Git；数据库文件也由 `.gitignore` 忽略。
