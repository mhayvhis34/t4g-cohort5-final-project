from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.repositories import student_repository

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("", response_model=schemas.StudentOut, status_code=status.HTTP_201_CREATED)
def create_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    existing = student_repository.get_by_email(db, student.email)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A student with email '{student.email}' already exists.",
        )
    return student_repository.create(db, student)


@router.get("", response_model=list[schemas.StudentOut])
def list_students(db: Session = Depends(get_db)):
    return student_repository.get_all(db)


@router.get("/{student_id}", response_model=schemas.StudentWithCourses)
def get_student(student_id: int, db: Session = Depends(get_db)):
    db_student = student_repository.get_by_id(db, student_id)
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found.",
        )
    return db_student


@router.put("/{student_id}", response_model=schemas.StudentOut)
def update_student(
    student_id: int, updates: schemas.StudentUpdate, db: Session = Depends(get_db)
):
    db_student = student_repository.get_by_id(db, student_id)
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found.",
        )
    if updates.email and updates.email != db_student.email:
        existing = student_repository.get_by_email(db, updates.email)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A student with email '{updates.email}' already exists.",
            )
    return student_repository.update(db, db_student, updates)


@router.delete("/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    db_student = student_repository.get_by_id(db, student_id)
    if not db_student:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Student with id {student_id} not found.",
        )
    student_repository.delete(db, db_student)
    return None
