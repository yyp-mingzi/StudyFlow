from pathlib import Path

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Project, Task, User


router = APIRouter()
templates = Jinja2Templates(
    directory=Path(__file__).resolve().parent.parent / "templates"
)


@router.get("/dashboard", response_class=HTMLResponse)
def dashboard(
    request: Request,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)

    active_project_count = db.scalar(
        select(func.count(Project.id)).where(
            Project.user_id == current_user.id,
            Project.status == "active",
        )
    ) or 0
    open_task_count = db.scalar(
        select(func.count(Task.id)).where(
            Task.user_id == current_user.id,
            Task.status != "completed",
        )
    ) or 0
    recent_tasks = list(
        db.scalars(
            select(Task)
            .where(Task.user_id == current_user.id)
            .order_by(Task.created_at.desc(), Task.id.desc())
            .limit(5)
        )
    )

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "username": current_user.username,
            "active_project_count": active_project_count,
            "open_task_count": open_task_count,
            "recent_tasks": recent_tasks,
        },
    )
