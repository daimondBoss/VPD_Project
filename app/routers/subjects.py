# app/routers/subjects.py
from uuid import UUID

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload

from app.database import SessionDep
from app.dependencies import CurrentUser
from app.models import Exam, Subject
from app.schemas import MAX_SUBJECTS, SubjectCreate, SubjectResponse, SubjectUpdate

router = APIRouter(prefix="/subjects", tags=["subjects"])


def _load_own_subject(subject_id: UUID, user_id: UUID, db) -> Subject:
    subject = db.scalar(
        select(Subject)
        .options(selectinload(Subject.exams))
        .where(Subject.id == subject_id, Subject.user_id == user_id)
    )
    if not subject:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Предмет не найден")
    return subject


def _to_response(s: Subject) -> SubjectResponse:
    exam = s.exams[0] if s.exams else None
    return SubjectResponse(
        id=s.id,
        title=s.title,
        color=s.color,
        created_at=s.created_at,
        exam_date=exam.exam_date if exam else None,
    )


@router.get("/", response_model=list[SubjectResponse])
def list_subjects(current_user: CurrentUser, db: SessionDep):
    subjects = db.scalars(
        select(Subject)
        .options(selectinload(Subject.exams))
        .where(Subject.user_id == current_user.id)
        .order_by(Subject.created_at.desc())
    ).all()
    return [_to_response(s) for s in subjects]


@router.post("/", response_model=SubjectResponse, status_code=201)
def create_subject(data: SubjectCreate, current_user: CurrentUser, db: SessionDep):
    count = db.scalar(
        select(func.count()).select_from(Subject).where(
            Subject.user_id == current_user.id
        )
    )
    if count >= MAX_SUBJECTS:
        raise HTTPException(
            status.HTTP_400_BAD_REQUEST,
            f"Нельзя добавить больше {MAX_SUBJECTS} предметов",
        )

    subject = Subject(user_id=current_user.id, title=data.title, color=data.color)
    db.add(subject)
    db.flush()
    db.add(Exam(subject_id=subject.id, exam_date=data.exam_date))
    db.commit()

    return _to_response(_load_own_subject(subject.id, current_user.id, db))


@router.patch("/{subject_id}", response_model=SubjectResponse)
def update_subject(
    subject_id: UUID,
    data: SubjectUpdate,
    current_user: CurrentUser,
    db: SessionDep,
):
    subject = _load_own_subject(subject_id, current_user.id, db)

    if data.title is not None:
        subject.title = data.title
    if data.color is not None:
        subject.color = data.color
    if data.exam_date is not None:
        if subject.exams:
            subject.exams[0].exam_date = data.exam_date
        else:
            db.add(Exam(subject_id=subject.id, exam_date=data.exam_date))

    db.commit()
    return _to_response(_load_own_subject(subject.id, current_user.id, db))


@router.delete("/{subject_id}", status_code=204)
def delete_subject(subject_id: UUID, current_user: CurrentUser, db: SessionDep):
    subject = _load_own_subject(subject_id, current_user.id, db)
    db.delete(subject)
    db.commit()