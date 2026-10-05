# StudyFlow

StudyFlow 是一个个人学习与项目工作台，面向学生和个人开发者。目前已完成 Day 1 的应用骨架，以及 Day 2 的数据库、首次账户初始化和基础认证流程。

## 环境要求

- Python 3.12 或更高版本

当前使用的主要技术：

- FastAPI 和 Uvicorn：后端应用与开发服务器
- Jinja2：HTML 页面模板
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
- Dashboard 提供退出登录按钮。

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

### 尚未实现

- Projects
- Tasks
- Study Plans
- Notes
- Study Logs
- Statistics
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
│   ├── main.py
│   ├── models.py
│   ├── routers/
│   │   ├── auth.py
│   │   └── dashboard.py
│   ├── static/
│   │   └── css/
│   │       └── style.css
│   └── templates/
│       ├── dashboard.html
│       ├── index.html
│       ├── login.html
│       └── setup.html
├── data/
│   └── studyflow.db
├── migrations/
│   ├── env.py
│   ├── script.py.mako
│   └── versions/
│       └── 0001_create_users_and_auth_sessions.py
├── pyproject.toml
└── README.md
```

`.venv/` 是本地虚拟环境目录，不纳入 Git；数据库文件也由 `.gitignore` 忽略。
