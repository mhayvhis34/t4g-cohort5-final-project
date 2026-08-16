from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import schemas
from app.database import get_db
from app.repositories import enrollment_repository, student_repository, course_repository

router = APIRouter(prefix="/enrollments", tags=["Enrollments"])


@router.post("", response_model=schemas.EnrollmentOut, status_code=status.HTTP_201_CREATED)
def create_enrollment(enrollment: schemas.EnrollmentCreate, db: Session = Depends(get_db)):
    student = student_repository.get_by_id(db, enrollment.student_id)
    if not student:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Student with id {enrollment.student_id} does not exist.",
        )

    course = course_repository.get_by_id(db, enrollment.course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Course with id {enrollment.course_id} does not exist.",
        )

    existing = enrollment_repository.get_by_student_and_course(
        db, enrollment.student_id, enrollment.course_id
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This student is already enrolled in this course.",
        )

    return enrollment_repository.create(db, enrollment)


@router.get("", response_model=list[schemas.EnrollmentOut])
def list_enrollments(
    student_id: Optional[int] = None,
    course_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    return enrollment_repository.get_all(db, student_id=student_id, course_id=course_id)


@router.get("/{enrollment_id}", response_model=schemas.EnrollmentOut)
def get_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    db_enrollment = enrollment_repository.get_by_id(db, enrollment_id)
    if not db_enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enrollment with id {enrollment_id} not found.",
        )
    return db_enrollment


@router.put("/{enrollment_id}", response_model=schemas.EnrollmentOut)
def update_enrollment(
    enrollment_id: int, updates: schemas.EnrollmentUpdate, db: Session = Depends(get_db)
):
    """Mainly used for recording/updating a student's grade in a course."""
    db_enrollment = enrollment_repository.get_by_id(db, enrollment_id)
    if not db_enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enrollment with id {enrollment_id} not found.",
        )
    return enrollment_repository.update(db, db_enrollment, updates)


@router.delete("/{enrollment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_enrollment(enrollment_id: int, db: Session = Depends(get_db)):
    """Unenrolls a student from a course."""
    db_enrollment = enrollment_repository.get_by_id(db, enrollment_id)
    if not db_enrollment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Enrollment with id {enrollment_id} not found.",
        )
    enrollment_repository.delete(db, db_enrollment)
    return None
