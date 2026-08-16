from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.repositories import course_repository

router = APIRouter(prefix="/courses", tags=["Courses"])


@router.post("", response_model=schemas.CourseOut, status_code=status.HTTP_201_CREATED)
def create_course(course: schemas.CourseCreate, db: Session = Depends(get_db)):
    existing = course_repository.get_by_code(db, course.code)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A course with code '{course.code}' already exists.",
        )
    return course_repository.create(db, course)


@router.get("", response_model=list[schemas.CourseOut])
def list_courses(db: Session = Depends(get_db)):
    return course_repository.get_all(db)


@router.get("/{course_id}", response_model=schemas.CourseWithStudents)
def get_course(course_id: int, db: Session = Depends(get_db)):
    db_course = course_repository.get_by_id(db, course_id)
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} not found.",
        )
    return db_course


@router.put("/{course_id}", response_model=schemas.CourseOut)
def update_course(
    course_id: int, updates: schemas.CourseUpdate, db: Session = Depends(get_db)
):
    db_course = course_repository.get_by_id(db, course_id)
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} not found.",
        )
    if updates.code and updates.code != db_course.code:
        existing = course_repository.get_by_code(db, updates.code)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"A course with code '{updates.code}' already exists.",
            )
    return course_repository.update(db, db_course, updates)


@router.delete("/{course_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_course(course_id: int, db: Session = Depends(get_db)):
    db_course = course_repository.get_by_id(db, course_id)
    if not db_course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Course with id {course_id} not found.",
        )
    course_repository.delete(db, db_course)
    return None
