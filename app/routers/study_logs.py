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
from app.models import StudyLog, Task, User
from app.schemas import StudyLogFormData


router = APIRouter()
templates = Jinja2Templates(
    directory=Path(__file__).resolve().parent.parent / "templates"
)


def get_owned_log(db: Session, log_id: int, user_id: int) -> StudyLog:
    log = db.scalar(
        select(StudyLog).where(
            StudyLog.id == log_id,
            StudyLog.user_id == user_id,
        )
    )
    if log is None:
        raise HTTPException(status_code=404, detail="Study log not found")
    return log


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


def render_study_log_form(
    request: Request,
    form: dict[str, str],
    tasks: list[Task],
    form_action: str,
    page_title: str,
    error: str | None = None,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="study_log_form.html",
        context={
            "form": form,
            "tasks": tasks,
            "form_action": form_action,
            "page_title": page_title,
            "error": error,
        },
        status_code=400 if error else 200,
    )


@router.get("/study-logs", response_class=HTMLResponse)
def list_study_logs(
    request: Request,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)

    log_rows = db.execute(
        select(StudyLog, Task.title)
        .outerjoin(
            Task,
            and_(
                Task.id == StudyLog.task_id,
                Task.user_id == StudyLog.user_id,
            ),
        )
        .where(StudyLog.user_id == current_user.id)
        .order_by(
            StudyLog.studied_on.desc(),
            StudyLog.created_at.desc(),
            StudyLog.id.desc(),
        )
    ).all()
    return templates.TemplateResponse(
        request=request,
        name="study_logs.html",
        context={"log_rows": log_rows},
    )


@router.get("/study-logs/new", response_class=HTMLResponse)
def new_study_log_page(
    request: Request,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)
    return render_study_log_form(
        request,
        {
            "studied_on": date.today().isoformat(),
            "duration_minutes": "30",
            "task_id": "",
            "note": "",
        },
        get_owned_tasks(db, current_user.id),
        "/study-logs",
        "新增学习记录",
    )


@router.post("/study-logs", response_class=HTMLResponse)
def create_study_log(
    request: Request,
    studied_on: str = Form(default=""),
    duration_minutes: str = Form(default=""),
    task_id: str = Form(default=""),
    note: str = Form(default=""),
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)

    tasks = get_owned_tasks(db, current_user.id)
    form = {
        "studied_on": studied_on,
        "duration_minutes": duration_minutes,
        "task_id": task_id,
        "note": note,
    }
    try:
        values = StudyLogFormData(**form)
    except ValidationError:
        return render_study_log_form(
            request,
            form,
            tasks,
            "/study-logs",
            "新增学习记录",
            "请填写有效日期和大于 0 的学习分钟数。",
        )

    if not task_belongs_to_user(db, values.task_id, current_user.id):
        return render_study_log_form(
            request,
            form,
            tasks,
            "/study-logs",
            "新增学习记录",
            "所选任务不存在或不属于当前用户。",
        )

    db.add(
        StudyLog(
            user_id=current_user.id,
            task_id=values.task_id,
            studied_on=values.studied_on,
            duration_minutes=values.duration_minutes,
            note=values.note,
        )
    )
    db.commit()
    return RedirectResponse(url="/study-logs", status_code=303)


@router.get("/study-logs/{log_id}/edit", response_class=HTMLResponse)
def edit_study_log_page(
    log_id: int,
    request: Request,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)
    log = get_owned_log(db, log_id, current_user.id)
    return render_study_log_form(
        request,
        {
            "studied_on": log.studied_on.isoformat(),
            "duration_minutes": str(log.duration_minutes),
            "task_id": str(log.task_id) if log.task_id is not None else "",
            "note": log.note or "",
        },
        get_owned_tasks(db, current_user.id),
        f"/study-logs/{log.id}/edit",
        "编辑学习记录",
    )


@router.post("/study-logs/{log_id}/edit", response_class=HTMLResponse)
def update_study_log(
    log_id: int,
    request: Request,
    studied_on: str = Form(default=""),
    duration_minutes: str = Form(default=""),
    task_id: str = Form(default=""),
    note: str = Form(default=""),
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)
    log = get_owned_log(db, log_id, current_user.id)
    tasks = get_owned_tasks(db, current_user.id)
    form = {
        "studied_on": studied_on,
        "duration_minutes": duration_minutes,
        "task_id": task_id,
        "note": note,
    }
    try:
        values = StudyLogFormData(**form)
    except ValidationError:
        return render_study_log_form(
            request,
            form,
            tasks,
            f"/study-logs/{log.id}/edit",
            "编辑学习记录",
            "请填写有效日期和大于 0 的学习分钟数。",
        )

    if not task_belongs_to_user(db, values.task_id, current_user.id):
        return render_study_log_form(
            request,
            form,
            tasks,
            f"/study-logs/{log.id}/edit",
            "编辑学习记录",
            "所选任务不存在或不属于当前用户。",
        )

    log.task_id = values.task_id
    log.studied_on = values.studied_on
    log.duration_minutes = values.duration_minutes
    log.note = values.note
    db.commit()
    return RedirectResponse(url="/study-logs", status_code=303)


@router.post("/study-logs/{log_id}/delete")
def delete_study_log(
    log_id: int,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)
    log = get_owned_log(db, log_id, current_user.id)
    db.delete(log)
    db.commit()
    return RedirectResponse(url="/study-logs", status_code=303)
