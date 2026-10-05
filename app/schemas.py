from datetime import date
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class ProjectFormData(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    name: str = Field(min_length=1, max_length=160)
    description: str | None = None
    status: Literal["active", "archived"] = "active"

    @field_validator("description", mode="before")
    @classmethod
    def blank_description_is_empty(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        return value


class TaskFormData(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    status: Literal["todo", "in_progress", "completed"] = "todo"
    priority: Literal["low", "medium", "high"] = "medium"
    project_id: int | None = None
    due_date: date | None = None

    @field_validator("description", mode="before")
    @classmethod
    def blank_description_is_empty(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        return value

    @field_validator("project_id", "due_date", mode="before")
    @classmethod
    def blank_optional_values_are_empty(cls, value: object) -> object:
        if value == "":
            return None
        return value


class StudyPlanFormData(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    plan_date: date
    planned_minutes: int = Field(gt=0, le=1440)
    task_id: int | None = Field(default=None, ge=1)

    @field_validator("description", mode="before")
    @classmethod
    def blank_description_is_empty(cls, value: str | None) -> str | None:
        if value is None or not value.strip():
            return None
        return value

    @field_validator("task_id", mode="before")
    @classmethod
    def blank_task_is_empty(cls, value: object) -> object:
        if value == "":
            return None
        return value


class NoteFormData(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    content_markdown: str = ""
    project_id: int | None = Field(default=None, ge=1)

    @field_validator("title", mode="before")
    @classmethod
    def strip_title(cls, value: object) -> object:
        if isinstance(value, str):
            return value.strip()
        return value

    @field_validator("project_id", mode="before")
    @classmethod
    def blank_project_is_empty(cls, value: object) -> object:
        if value == "":
            return None
        return value
