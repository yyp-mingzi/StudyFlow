import os
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.routers.auth import router as auth_router
from app.routers.dashboard import router as dashboard_router


APP_DIRECTORY = Path(__file__).resolve().parent
APP_NAME = os.getenv("STUDYFLOW_APP_NAME", "StudyFlow")

app = FastAPI(title=APP_NAME)
app.mount(
    "/static",
    StaticFiles(directory=APP_DIRECTORY / "static"),
    name="static",
)
templates = Jinja2Templates(directory=APP_DIRECTORY / "templates")
app.include_router(auth_router)
app.include_router(dashboard_router)


@app.get("/", include_in_schema=False)
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"app_name": APP_NAME},
    )
