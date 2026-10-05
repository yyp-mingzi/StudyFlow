# StudyFlow

StudyFlow 是一个个人学习与项目工作台。当前是 Day 1 的启动骨架：FastAPI 提供首页，页面使用 HTML 模板和基础 CSS。

## 环境要求

- Python 3.11 或更高版本

## 安装与启动（Windows PowerShell）

在项目根目录执行：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -e .
python -m uvicorn app.main:app --reload
```

打开 <http://127.0.0.1:8000> 查看 StudyFlow 首页。开发服务器启动后修改文件会自动重新加载。

如果 PowerShell 找不到可用的 `python` 命令，先将本机 Python 3.11 的安装目录加入 `PATH`；也可以把下面示例中的路径替换为本机的 `python.exe` 完整路径来创建虚拟环境：

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

Day 1 只包含可启动的网页骨架。登录、数据库、任务、项目、计划、笔记和学习记录将在后续阶段按计划逐步开发。
