from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Query, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError
from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.database import get_db
from app.markdown_utils import render_markdown
from app.models import Note, Project, User
from app.schemas import NoteFormData


router = APIRouter()
templates = Jinja2Templates(
    directory=Path(__file__).resolve().parent.parent / "templates"
)


def get_owned_note(db: Session, note_id: int, user_id: int) -> Note:
    note = db.scalar(
        select(Note).where(
            Note.id == note_id,
            Note.user_id == user_id,
        )
    )
    if note is None:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


def get_owned_projects(db: Session, user_id: int) -> list[Project]:
    return list(
        db.scalars(
            select(Project)
            .where(Project.user_id == user_id)
            .order_by(Project.name, Project.id)
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


def render_note_form(
    request: Request,
    form: dict[str, str],
    projects: list[Project],
    form_action: str,
    page_title: str,
    error: str | None = None,
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="note_form.html",
        context={
            "form": form,
            "projects": projects,
            "form_action": form_action,
            "page_title": page_title,
            "error": error,
        },
        status_code=400 if error else 200,
    )


@router.get("/notes", response_class=HTMLResponse)
def list_notes(
    request: Request,
    q: str = Query(default=""),
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)

    search_term = q.strip()
    query = (
        select(Note, Project.name)
        .outerjoin(
            Project,
            and_(
                Project.id == Note.project_id,
                Project.user_id == Note.user_id,
            ),
        )
        .where(Note.user_id == current_user.id)
        .order_by(Note.updated_at.desc(), Note.id.desc())
    )
    if search_term:
        query = query.where(Note.title.contains(search_term, autoescape=True))

    note_rows = db.execute(query).all()
    return templates.TemplateResponse(
        request=request,
        name="notes.html",
        context={"note_rows": note_rows, "search_term": search_term},
    )


@router.get("/notes/new", response_class=HTMLResponse)
def new_note_page(
    request: Request,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)
    return render_note_form(
        request,
        {"title": "", "content_markdown": "", "project_id": ""},
        get_owned_projects(db, current_user.id),
        "/notes",
        "新建笔记",
    )


@router.post("/notes", response_class=HTMLResponse)
def create_note(
    request: Request,
    title: str = Form(default=""),
    content_markdown: str = Form(default=""),
    project_id: str = Form(default=""),
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)

    projects = get_owned_projects(db, current_user.id)
    form = {
        "title": title,
        "content_markdown": content_markdown,
        "project_id": project_id,
    }
    try:
        values = NoteFormData(**form)
    except ValidationError:
        return render_note_form(
            request,
            form,
            projects,
            "/notes",
            "新建笔记",
            "请输入非空标题，并选择属于自己的项目。",
        )

    if not project_belongs_to_user(db, values.project_id, current_user.id):
        return render_note_form(
            request,
            form,
            projects,
            "/notes",
            "新建笔记",
            "所选项目不存在或不属于当前用户。",
        )

    note = Note(
        user_id=current_user.id,
        project_id=values.project_id,
        title=values.title,
        content_markdown=values.content_markdown,
    )
    db.add(note)
    db.commit()
    return RedirectResponse(url=f"/notes/{note.id}", status_code=303)


@router.get("/notes/{note_id}", response_class=HTMLResponse)
def note_detail(
    note_id: int,
    request: Request,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)

    row = db.execute(
        select(Note, Project.name)
        .outerjoin(
            Project,
            and_(
                Project.id == Note.project_id,
                Project.user_id == Note.user_id,
            ),
        )
        .where(
            Note.id == note_id,
            Note.user_id == current_user.id,
        )
    ).one_or_none()
    if row is None:
        raise HTTPException(status_code=404, detail="Note not found")

    note, project_name = row
    return templates.TemplateResponse(
        request=request,
        name="note_detail.html",
        context={
            "note": note,
            "project_name": project_name,
            "rendered_markdown": render_markdown(note.content_markdown),
        },
    )


@router.get("/notes/{note_id}/edit", response_class=HTMLResponse)
def edit_note_page(
    note_id: int,
    request: Request,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)
    note = get_owned_note(db, note_id, current_user.id)
    return render_note_form(
        request,
        {
            "title": note.title,
            "content_markdown": note.content_markdown,
            "project_id": str(note.project_id) if note.project_id is not None else "",
        },
        get_owned_projects(db, current_user.id),
        f"/notes/{note.id}/edit",
        "编辑笔记",
    )


@router.post("/notes/{note_id}/edit", response_class=HTMLResponse)
def update_note(
    note_id: int,
    request: Request,
    title: str = Form(default=""),
    content_markdown: str = Form(default=""),
    project_id: str = Form(default=""),
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)
    note = get_owned_note(db, note_id, current_user.id)
    projects = get_owned_projects(db, current_user.id)
    form = {
        "title": title,
        "content_markdown": content_markdown,
        "project_id": project_id,
    }
    try:
        values = NoteFormData(**form)
    except ValidationError:
        return render_note_form(
            request,
            form,
            projects,
            f"/notes/{note.id}/edit",
            "编辑笔记",
            "请输入非空标题，并选择属于自己的项目。",
        )

    if not project_belongs_to_user(db, values.project_id, current_user.id):
        return render_note_form(
            request,
            form,
            projects,
            f"/notes/{note.id}/edit",
            "编辑笔记",
            "所选项目不存在或不属于当前用户。",
        )

    note.project_id = values.project_id
    note.title = values.title
    note.content_markdown = values.content_markdown
    db.commit()
    return RedirectResponse(url=f"/notes/{note.id}", status_code=303)


@router.post("/notes/{note_id}/delete")
def delete_note(
    note_id: int,
    current_user: User | None = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user is None:
        return RedirectResponse(url="/login", status_code=303)
    note = get_owned_note(db, note_id, current_user.id)
    db.delete(note)
    db.commit()
    return RedirectResponse(url="/notes", status_code=303)
