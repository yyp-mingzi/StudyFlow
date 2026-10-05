from datetime import date
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.models import StudyPlan, Task, User
from app.schemas import StudyPlanFormData


router = APIRouter()
templates = Jinja2Templates(
    directory=Path(__file__).resolve().parent.parent / "templates"
)


def get_owned_plan(db: Session, plan_id: int, user_id: int) -> StudyPlan:
    plan = db.scalar(
        select(StudyPlan).where(
            StudyPlan.id == plan_id,
            StudyPlan.user_id == user_id,
        )
    )
    if plan is None:
        raise HTTPException(status_code=404, detail="Study plan not found")
    return plan


def get_owned_tasks(db: Session, user_id: int) -> list[Task]:
    return list(
        db.scalars(
            select(Task)
            .where(Task.user_id == user_id)
            .order_by(Task.title, Task.id)
        )
    )


def task_belongs_to_user(db: Session, task_id: int | None, user_id: int) -> bool:
    if task_id is None:
        return True
    return (
        db.scalar(
            select(Task.id).where(
                Task.id == task_id,
                Task.user_id == user_id,
            )
        )
        is not None
    )


def render_plan_form(
    request: Request,
    form: dict[str, str],
    tasks: list[Task],
    form_action: str,
    page_title: str,
    error: str | None = None,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="plan_form.html",
        context={
            "form": form,
            "tasks": tasks,
            "form_action": form_action,
            "page_title": page_title,
            "error": error,
        },
        status_code=400 if error else 200,
    )


@router.get("/plans", response_class=HTMLResponse)
def list_plans(
    request: Request,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)

    plan_rows = db.execute(
        select(StudyPlan, Task.title)
        .outerjoin(
            Task,
            and_(
                Task.id == StudyPlan.task_id,
                Task.user_id == StudyPlan.user_id,
            ),
        )
        .where(StudyPlan.user_id == current_user.id)
        .order_by(StudyPlan.plan_date, StudyPlan.id.desc())
    ).all()
    return templates.TemplateResponse(
        request=request,
        name="plans.html",
        context={"plan_rows": plan_rows},
    )


@router.get("/plans/new", response_class=HTMLResponse)
def new_plan_page(
    request: Request,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)
    return render_plan_form(
        request,
        {
            "title": "",
            "description": "",
            "plan_date": date.today().isoformat(),
            "planned_minutes": "60",
            "task_id": "",
        },
        get_owned_tasks(db, current_user.id),
        "/plans",
        "新建学习计划",
    )


@router.post("/plans", response_class=HTMLResponse)
def create_plan(
    request: Request,
    title: str = Form(default=""),
    description: str = Form(default=""),
    plan_date: str = Form(default=""),
    planned_minutes: str = Form(default=""),
    task_id: str = Form(default=""),
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)

    tasks = get_owned_tasks(db, current_user.id)
    form = {
        "title": title,
        "description": description,
        "plan_date": plan_date,
        "planned_minutes": planned_minutes,
        "task_id": task_id,
    }
    try:
        values = StudyPlanFormData(**form)
    except ValidationError:
        return render_plan_form(
            request,
            form,
            tasks,
            "/plans",
            "新建学习计划",
            "请填写有效的标题、日期和分钟数（1 至 1440 分钟）。",
        )

    if not task_belongs_to_user(db, values.task_id, current_user.id):
        return render_plan_form(
            request,
            form,
            tasks,
            "/plans",
            "新建学习计划",
            "所选任务不存在或不属于当前用户。",
        )

    db.add(
        StudyPlan(
            user_id=current_user.id,
            task_id=values.task_id,
            title=values.title,
            description=values.description,
            plan_date=values.plan_date,
            planned_minutes=values.planned_minutes,
        )
    )
    db.commit()
    return RedirectResponse(url="/plans", status_code=303)


@router.get("/plans/{plan_id}/edit", response_class=HTMLResponse)
def edit_plan_page(
    plan_id: int,
    request: Request,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)
    plan = get_owned_plan(db, plan_id, current_user.id)
    return render_plan_form(
        request,
        {
            "title": plan.title,
            "description": plan.description or "",
            "plan_date": plan.plan_date.isoformat(),
            "planned_minutes": str(plan.planned_minutes),
            "task_id": str(plan.task_id) if plan.task_id is not None else "",
        },
        get_owned_tasks(db, current_user.id),
        f"/plans/{plan.id}/edit",
        "编辑学习计划",
    )


@router.post("/plans/{plan_id}/edit", response_class=HTMLResponse)
def update_plan(
    plan_id: int,
    request: Request,
    title: str = Form(default=""),
    description: str = Form(default=""),
    plan_date: str = Form(default=""),
    planned_minutes: str = Form(default=""),
    task_id: str = Form(default=""),
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)
    plan = get_owned_plan(db, plan_id, current_user.id)
    tasks = get_owned_tasks(db, current_user.id)
    form = {
        "title": title,
        "description": description,
        "plan_date": plan_date,
        "planned_minutes": planned_minutes,
        "task_id": task_id,
    }
    try:
        values = StudyPlanFormData(**form)
    except ValidationError:
        return render_plan_form(
            request,
            form,
            tasks,
            f"/plans/{plan.id}/edit",
            "编辑学习计划",
            "请填写有效的标题、日期和分钟数（1 至 1440 分钟）。",
        )

    if not task_belongs_to_user(db, values.task_id, current_user.id):
        return render_plan_form(
            request,
            form,
            tasks,
            f"/plans/{plan.id}/edit",
            "编辑学习计划",
            "所选任务不存在或不属于当前用户。",
        )

    plan.task_id = values.task_id
    plan.title = values.title
    plan.description = values.description
    plan.plan_date = values.plan_date
    plan.planned_minutes = values.planned_minutes
    db.commit()
    return RedirectResponse(url="/plans", status_code=303)


@router.post("/plans/{plan_id}/delete")
def delete_plan(
    plan_id: int,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)
    plan = get_owned_plan(db, plan_id, current_user.id)
    db.delete(plan)
    db.commit()
    return RedirectResponse(url="/plans", status_code=303)
