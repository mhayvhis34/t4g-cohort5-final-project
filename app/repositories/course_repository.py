"""
Repository layer for Course.
Keeps raw database queries out of the route handlers.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app import models, schemas


def get_all(db: Session) -> List[models.Course]:
    return db.query(models.Course).all()


def get_by_id(db: Session, course_id: int) -> Optional[models.Course]:
    return db.query(models.Course).filter(models.Course.id == course_id).first()


def get_by_code(db: Session, code: str) -> Optional[models.Course]:
    return db.query(models.Course).filter(models.Course.code == code).first()


def create(db: Session, course: schemas.CourseCreate) -> models.Course:
    db_course = models.Course(**course.model_dump())
    db.add(db_course)
    db.commit()
    db.refresh(db_course)
    return db_course


def update(
    db: Session, db_course: models.Course, updates: schemas.CourseUpdate
) -> models.Course:
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(db_course, field, value)
    db.commit()
    db.refresh(db_course)
    return db_course


def delete(db: Session, db_course: models.Course) -> None:
    db.delete(db_course)
    db.commit()
