from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Note, Project, Task, User
from app.schemas import ProjectFormData


router = APIRouter()
templates = Jinja2Templates(
    directory=Path(__file__).resolve().parent.parent / "templates"
)


def render_project_form(
    request: Request,
    form: dict[str, str],
    form_action: str,
    page_title: str,
    error: str | None = None,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="project_form.html",
        context={
            "form": form,
            "form_action": form_action,
            "page_title": page_title,
            "error": error,
        },
        status_code=400 if error else 200,
    )


def get_owned_project(db: Session, project_id: int, user_id: int) -> Project:
    project = db.scalar(
        select(Project).where(
            Project.id == project_id,
            Project.user_id == user_id,
        )
    )
    if project is None:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.get("/projects", response_class=HTMLResponse)
def list_projects(
    request: Request,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)

    projects = list(
        db.scalars(
            select(Project)
            .where(Project.user_id == current_user.id)
            .order_by(Project.created_at.desc(), Project.id.desc())
        )
    )
    return templates.TemplateResponse(
        request=request,
        name="projects.html",
        context={"projects": projects},
    )


@router.get("/projects/new", response_class=HTMLResponse)
def new_project_page(
    request: Request,
    current_user: User | None = Depends(get_current_user),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)
    return render_project_form(
        request,
        {"name": "", "description": "", "status": "active"},
        "/projects",
        "新建项目",
    )


@router.post("/projects", response_class=HTMLResponse)
def create_project(
    request: Request,
    name: str = Form(default=""),
    description: str = Form(default=""),
    status: str = Form(default="active"),
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)

    form = {"name": name, "description": description, "status": status}
    try:
        values = ProjectFormData(**form)
    except ValidationError:
        message = "项目名称不能为空，且状态必须是有效选项。"
        return render_project_form(request, form, "/projects", "新建项目", message)

    db.add(
        Project(
            user_id=current_user.id,
            name=values.name,
            description=values.description,
            status=values.status,
        )
    )
    db.commit()
    return RedirectResponse(url="/projects", status_code=303)


@router.get("/projects/{project_id}/edit", response_class=HTMLResponse)
def edit_project_page(
    project_id: int,
    request: Request,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)
    project = get_owned_project(db, project_id, current_user.id)
    form = {
        "name": project.name,
        "description": project.description or "",
        "status": project.status,
    }
    return render_project_form(
        request,
        form,
        f"/projects/{project.id}/edit",
        "编辑项目",
    )


@router.post("/projects/{project_id}/edit", response_class=HTMLResponse)
def update_project(
    project_id: int,
    request: Request,
    name: str = Form(default=""),
    description: str = Form(default=""),
    status: str = Form(default="active"),
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)
    project = get_owned_project(db, project_id, current_user.id)

    form = {"name": name, "description": description, "status": status}
    try:
        values = ProjectFormData(**form)
    except ValidationError:
        message = "项目名称不能为空，且状态必须是有效选项。"
        return render_project_form(
            request,
            form,
            f"/projects/{project.id}/edit",
            "编辑项目",
            message,
        )

    project.name = values.name
    project.description = values.description
    project.status = values.status
    db.commit()
    return RedirectResponse(url="/projects", status_code=303)


@router.post("/projects/{project_id}/archive")
def archive_project(
    project_id: int,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)
    project = get_owned_project(db, project_id, current_user.id)
    project.status = "archived"
    db.commit()
    return RedirectResponse(url="/projects", status_code=303)


@router.post("/projects/{project_id}/delete")
def delete_project(
    project_id: int,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)
    project = get_owned_project(db, project_id, current_user.id)

    # Tasks remain available when their optional project is removed.
    db.execute(
        update(Task)
        .where(
            Task.user_id == current_user.id,
            Task.project_id == project.id,
        )
        .values(project_id=None, updated_at=datetime.now(timezone.utc))
    )
    db.execute(
        update(Note)
        .where(
            Note.user_id == current_user.id,
            Note.project_id == project.id,
        )
        .values(project_id=None, updated_at=datetime.now(timezone.utc))
    )
    db.delete(project)
    db.commit()
    return RedirectResponse(url="/projects", status_code=303)
