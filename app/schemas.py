# app/schemas.py
from datetime import date, datetime, timedelta
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

MAX_SUBJECTS = 10


# ---------- Auth ----------

class UserRegister(BaseModel):
    email: EmailStr
    password: Annotated[str, Field(min_length=8, max_length=72)]
    name: str | None = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    name: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


# ---------- Subject ----------

def _exam_date_not_before_tomorrow(v: date) -> date:
    if v < date.today() + timedelta(days=1):
        raise ValueError("Дата экзамена не может быть раньше завтрашнего дня")
    return v


class SubjectCreate(BaseModel):
    title: Annotated[str, Field(min_length=1, max_length=100)]
    color: str | None = None
    exam_date: date

    @field_validator("exam_date")
    @classmethod
    def _check(cls, v: date) -> date:
        return _exam_date_not_before_tomorrow(v)


class SubjectUpdate(BaseModel):
    title: Annotated[str | None, Field(min_length=1, max_length=100)] = None
    color: str | None = None
    exam_date: date | None = None

    @field_validator("exam_date")
    @classmethod
    def _check(cls, v: date | None) -> date | None:
        return _exam_date_not_before_tomorrow(v) if v is not None else v


class SubjectResponse(BaseModel):
    id: UUID
    title: str
    color: str | None = None
    exam_date: date | None = None
    created_at: datetime