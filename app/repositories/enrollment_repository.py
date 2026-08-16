"""
Repository layer for Enrollment (the Student <-> Course join).
Keeps raw database queries out of the route handlers.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app import models, schemas


def get_all(
    db: Session, student_id: Optional[int] = None, course_id: Optional[int] = None
) -> List[models.Enrollment]:
    query = db.query(models.Enrollment)
    if student_id is not None:
        query = query.filter(models.Enrollment.student_id == student_id)
    if course_id is not None:
        query = query.filter(models.Enrollment.course_id == course_id)
    return query.all()


def get_by_id(db: Session, enrollment_id: int) -> Optional[models.Enrollment]:
    return (
        db.query(models.Enrollment)
        .filter(models.Enrollment.id == enrollment_id)
        .first()
    )


def get_by_student_and_course(
    db: Session, student_id: int, course_id: int
) -> Optional[models.Enrollment]:
    return (
        db.query(models.Enrollment)
        .filter(
            models.Enrollment.student_id == student_id,
            models.Enrollment.course_id == course_id,
        )
        .first()
    )


def create(db: Session, enrollment: schemas.EnrollmentCreate) -> models.Enrollment:
    db_enrollment = models.Enrollment(**enrollment.model_dump())
    db.add(db_enrollment)
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment


def update(
    db: Session,
    db_enrollment: models.Enrollment,
    updates: schemas.EnrollmentUpdate,
) -> models.Enrollment:
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(db_enrollment, field, value)
    db.commit()
    db.refresh(db_enrollment)
    return db_enrollment


def delete(db: Session, db_enrollment: models.Enrollment) -> None:
    db.delete(db_enrollment)
    db.commit()
