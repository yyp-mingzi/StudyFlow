from pathlib import Path
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import delete, select, text
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth import (
    SESSION_COOKIE_NAME,
    SESSION_LIFETIME,
    SESSION_SAME_SITE,
    create_session_token,
    get_current_user,
    hash_session_token,
    password_hash,
    verify_password,
)
from app.database import get_db
from app.models import AuthSession, User


router = APIRouter()
templates = Jinja2Templates(
    directory=Path(__file__).resolve().parent.parent / "templates"
)


def render_setup(
    request: Request,
    error: str | None = None,
    username: str = "",
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="setup.html",
        context={"error": error, "username": username},
        status_code=400 if error else 200,
    )


def redirect_to_login() -> RedirectResponse:
    return RedirectResponse(url="/login", status_code=303)


def render_login(
    request: Request,
    error: str | None = None,
    username: str = "",
) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="login.html",
        context={"error": error, "username": username},
        status_code=401 if error else 200,
    )


@router.get("/setup", response_class=HTMLResponse)
def setup_page(request: Request, db: Session = Depends(get_db)):
    existing_user_id = db.scalar(select(User.id).limit(1))
    if existing_user_id is not None:
        return redirect_to_login()

    return render_setup(request)


@router.post("/setup", response_class=HTMLResponse)
def create_first_account(
    request: Request,
    username: str = Form(default=""),
    password: str = Form(default=""),
    confirm_password: str = Form(default=""),
    db: Session = Depends(get_db),
):
    username = username.strip()

    if db.scalar(select(User.id).limit(1)) is not None:
        db.rollback()
        return redirect_to_login()

    if not username:
        return render_setup(request, "请输入用户名。")
    if not password:
        return render_setup(request, "请输入密码。", username)
    if password != confirm_password:
        return render_setup(request, "两次输入的密码不一致。", username)

    hashed_password = password_hash(password)

    try:
        # Serialize first-account creation so concurrent requests cannot both
        # observe an empty users table and create separate accounts.
        db.execute(text("BEGIN IMMEDIATE"))
        if db.scalar(select(User.id).limit(1)) is not None:
            db.rollback()
            return redirect_to_login()

        db.add(User(username=username, password_hash=hashed_password))
        db.commit()
    except IntegrityError:
        db.rollback()
        return render_setup(request, "该用户名已被使用，请换一个。", username)

    return redirect_to_login()


@router.get("/login", response_class=HTMLResponse)
def login_page(
    request: Request,
    current_user: User | None = Depends(get_current_user),
):
    if current_user is not None:
        return RedirectResponse(url="/dashboard", status_code=303)
    return render_login(request)


@router.post("/login", response_class=HTMLResponse)
def login(
    request: Request,
    username: str = Form(default=""),
    password: str = Form(default=""),
    db: Session = Depends(get_db),
):
    username = username.strip()
    user = db.scalar(select(User).where(User.username == username))
    if user is None or not verify_password(password, user.password_hash):
        return render_login(request, "用户名或密码错误。", username)

    token = create_session_token()
    now = datetime.now(timezone.utc)
    expires_at = now + SESSION_LIFETIME

    # Serialize session replacement so a user cannot end up with two valid
    # sessions when two login requests arrive at the same time.
    db.execute(text("BEGIN IMMEDIATE"))
    db.execute(delete(AuthSession).where(AuthSession.user_id == user.id))
    db.add(
        AuthSession(
            user_id=user.id,
            token_hash=hash_session_token(token),
            created_at=now,
            expires_at=expires_at,
        )
    )
    db.commit()

    response = RedirectResponse(url="/dashboard", status_code=303)
    response.set_cookie(
        key=SESSION_COOKIE_NAME,
        value=token,
        max_age=int(SESSION_LIFETIME.total_seconds()),
        expires=expires_at,
        httponly=True,
        secure=request.url.scheme == "https",
        samesite=SESSION_SAME_SITE,
        path="/",
    )
    return response


@router.post("/logout")
def logout(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token:
        auth_session = db.scalar(
            select(AuthSession).where(
                AuthSession.token_hash == hash_session_token(token),
            )
        )
        if auth_session is not None:
            db.delete(auth_session)
            db.commit()

    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie(
        key=SESSION_COOKIE_NAME,
        path="/",
        secure=request.url.scheme == "https",
        httponly=True,
        samesite=SESSION_SAME_SITE,
    )
    return response
