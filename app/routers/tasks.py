from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Project, Task, User
from app.schemas import TaskFormData


router = APIRouter()
templates = Jinja2Templates(
    directory=Path(__file__).resolve().parent.parent / "templates"
)


def render_task_form(
    request: Request,
    form: dict[str, str],
    projects: list[Project],
    form_action: str,
    page_title: str,
    error: str | None = None,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="task_form.html",
        context={
            "form": form,
            "projects": projects,
            "form_action": form_action,
            "page_title": page_title,
            "error": error,
        },
        status_code=400 if error else 200,
    )


def get_owned_task(db: Session, task_id: int, user_id: int) -> Task:
    task = db.scalar(
        select(Task).where(
            Task.id == task_id,
            Task.user_id == user_id,
        )
    )
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


def get_owned_projects(db: Session, user_id: int) -> list[Project]:
    return list(
        db.scalars(
            select(Project)
            .where(Project.user_id == user_id)
            .order_by(Project.name)
        )
    )


def project_belongs_to_user(
    db: Session,
    project_id: int | None,
    user_id: int,
) -> bool:
    if project_id is None:
        return True
    return (
        db.scalar(
            select(Project.id).where(
                Project.id == project_id,
                Project.user_id == user_id,
            )
        )
        is not None
    )


@router.get("/tasks", response_class=HTMLResponse)
def list_tasks(
    request: Request,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)

    task_rows = db.execute(
        select(Task, Project.name)
        .outerjoin(
            Project,
            and_(
                Project.id == Task.project_id,
                Project.user_id == Task.user_id,
            ),
        )
        .where(Task.user_id == current_user.id)
        .order_by(Task.created_at.desc(), Task.id.desc())
    ).all()
    return templates.TemplateResponse(
        request=request,
        name="tasks.html",
        context={"task_rows": task_rows},
    )


@router.get("/tasks/new", response_class=HTMLResponse)
def new_task_page(
    request: Request,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)
    return render_task_form(
        request,
        {
            "title": "",
            "description": "",
            "status": "todo",
            "priority": "medium",
            "project_id": "",
            "due_date": "",
        },
        get_owned_projects(db, current_user.id),
        "/tasks",
        "新建任务",
    )


@router.post("/tasks", response_class=HTMLResponse)
def create_task(
    request: Request,
    title: str = Form(default=""),
    description: str = Form(default=""),
    status: str = Form(default="todo"),
    priority: str = Form(default="medium"),
    project_id: str = Form(default=""),
    due_date: str = Form(default=""),
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)

    projects = get_owned_projects(db, current_user.id)
    form = {
        "title": title,
        "description": description,
        "status": status,
        "priority": priority,
        "project_id": project_id,
        "due_date": due_date,
    }
    try:
        values = TaskFormData(**form)
    except ValidationError:
        return render_task_form(
            request,
            form,
            projects,
            "/tasks",
            "新建任务",
            "请填写有效的任务标题、状态、优先级和截止日期。",
        )

    if not project_belongs_to_user(db, values.project_id, current_user.id):
        return render_task_form(
            request,
            form,
            projects,
            "/tasks",
            "新建任务",
            "所选项目不存在或不属于当前用户。",
        )

    now = datetime.now(timezone.utc)
    db.add(
        Task(
            user_id=current_user.id,
            project_id=values.project_id,
            title=values.title,
            description=values.description,
            status=values.status,
            priority=values.priority,
            due_date=values.due_date,
            completed_at=now if values.status == "completed" else None,
        )
    )
    db.commit()
    return RedirectResponse(url="/tasks", status_code=303)


@router.get("/tasks/{task_id}/edit", response_class=HTMLResponse)
def edit_task_page(
    task_id: int,
    request: Request,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)
    task = get_owned_task(db, task_id, current_user.id)
    form = {
        "title": task.title,
        "description": task.description or "",
        "status": task.status,
        "priority": task.priority,
        "project_id": str(task.project_id) if task.project_id is not None else "",
        "due_date": task.due_date.isoformat() if task.due_date else "",
    }
    return render_task_form(
        request,
        form,
        get_owned_projects(db, current_user.id),
        f"/tasks/{task.id}/edit",
        "编辑任务",
    )


@router.post("/tasks/{task_id}/edit", response_class=HTMLResponse)
def update_task(
    task_id: int,
    request: Request,
    title: str = Form(default=""),
    description: str = Form(default=""),
    status: str = Form(default="todo"),
    priority: str = Form(default="medium"),
    project_id: str = Form(default=""),
    due_date: str = Form(default=""),
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)
    task = get_owned_task(db, task_id, current_user.id)

    projects = get_owned_projects(db, current_user.id)
    form = {
        "title": title,
        "description": description,
        "status": status,
        "priority": priority,
        "project_id": project_id,
        "due_date": due_date,
    }
    try:
        values = TaskFormData(**form)
    except ValidationError:
        return render_task_form(
            request,
            form,
            projects,
            f"/tasks/{task.id}/edit",
            "编辑任务",
            "请填写有效的任务标题、状态、优先级和截止日期。",
        )

    if not project_belongs_to_user(db, values.project_id, current_user.id):
        return render_task_form(
            request,
            form,
            projects,
            f"/tasks/{task.id}/edit",
            "编辑任务",
            "所选项目不存在或不属于当前用户。",
        )

    now = datetime.now(timezone.utc)
    if values.status == "completed":
        if task.status != "completed" or task.completed_at is None:
            task.completed_at = now
    else:
        task.completed_at = None

    task.project_id = values.project_id
    task.title = values.title
    task.description = values.description
    task.status = values.status
    task.priority = values.priority
    task.due_date = values.due_date
    db.commit()
    return RedirectResponse(url="/tasks", status_code=303)


@router.post("/tasks/{task_id}/complete")
def complete_task(
    task_id: int,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)
    task = get_owned_task(db, task_id, current_user.id)
    if task.status != "completed" or task.completed_at is None:
        task.status = "completed"
        task.completed_at = datetime.now(timezone.utc)
        db.commit()
    return RedirectResponse(url="/tasks", status_code=303)


@router.post("/tasks/{task_id}/delete")
def delete_task(
    task_id: int,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)
    task = get_owned_task(db, task_id, current_user.id)
    db.delete(task)
    db.commit()
    return RedirectResponse(url="/tasks", status_code=303)
