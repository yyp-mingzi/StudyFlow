from pathlib import Path
from datetime import date

from fastapi import APIRouter, Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import and_, func, select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import Project, StudyPlan, Task, User


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
    today = date.today()
    today_open_tasks = list(
        db.scalars(
            select(Task)
            .where(
                Task.user_id == current_user.id,
                Task.due_date == today,
                Task.status != "completed",
            )
            .order_by(Task.id)
        )
    )
    today_plan_rows = db.execute(
        select(StudyPlan, Task.title)
        .outerjoin(
            Task,
            and_(
                Task.id == StudyPlan.task_id,
                Task.user_id == StudyPlan.user_id,
            ),
        )
        .where(
            StudyPlan.user_id == current_user.id,
            StudyPlan.plan_date == today,
        )
        .order_by(StudyPlan.id)
    ).all()
    today_plan_minutes = db.scalar(
        select(func.coalesce(func.sum(StudyPlan.planned_minutes), 0)).where(
            StudyPlan.user_id == current_user.id,
            StudyPlan.plan_date == today,
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
            "today": today,
            "today_open_tasks": today_open_tasks,
            "today_open_task_count": len(today_open_tasks),
            "today_plan_rows": today_plan_rows,
            "today_plan_minutes": today_plan_minutes,
            "recent_tasks": recent_tasks,
        },
    )
