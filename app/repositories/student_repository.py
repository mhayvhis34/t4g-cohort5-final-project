"""
Repository layer for Student.
Keeps raw database queries out of the route handlers.
"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app import models, schemas


def get_all(db: Session) -> List[models.Student]:
    return db.query(models.Student).all()


def get_by_id(db: Session, student_id: int) -> Optional[models.Student]:
    return db.query(models.Student).filter(models.Student.id == student_id).first()


def get_by_email(db: Session, email: str) -> Optional[models.Student]:
    return db.query(models.Student).filter(models.Student.email == email).first()


def create(db: Session, student: schemas.StudentCreate) -> models.Student:
    db_student = models.Student(**student.model_dump())
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return db_student


def update(
    db: Session, db_student: models.Student, updates: schemas.StudentUpdate
) -> models.Student:
    for field, value in updates.model_dump(exclude_unset=True).items():
        setattr(db_student, field, value)
    db.commit()
    db.refresh(db_student)
    return db_student


def delete(db: Session, db_student: models.Student) -> None:
    db.delete(db_student)
    db.commit()
