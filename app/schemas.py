"""
Pydantic schemas used for request validation and response shaping.
Kept separate from the SQLAlchemy models so we control exactly what
goes in/out of the API (hide internal fields, nest related objects,
make fields optional on update, etc).
"""

from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr, ConfigDict


# ---------- Course (referenced by Enrollment / Student schemas below) ----------

class CourseBase(BaseModel):
    code: str = Field(..., min_length=1, max_length=20)
    title: str = Field(..., min_length=1, max_length=150)
    description: Optional[str] = None
    credits: int = Field(3, ge=1, le=12)


class CourseCreate(CourseBase):
    pass


class CourseUpdate(BaseModel):
    code: Optional[str] = Field(None, min_length=1, max_length=20)
    title: Optional[str] = Field(None, min_length=1, max_length=150)
    description: Optional[str] = None
    credits: Optional[int] = Field(None, ge=1, le=12)


class CourseOut(CourseBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Student ----------

class StudentBase(BaseModel):
    first_name: str = Field(..., min_length=1, max_length=80)
    last_name: str = Field(..., min_length=1, max_length=80)
    email: EmailStr
    date_of_birth: Optional[date] = None
    phone: Optional[str] = Field(None, max_length=30)


class StudentCreate(StudentBase):
    pass


class StudentUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=80)
    last_name: Optional[str] = Field(None, min_length=1, max_length=80)
    email: Optional[EmailStr] = None
    date_of_birth: Optional[date] = None
    phone: Optional[str] = Field(None, max_length=30)


class StudentOut(StudentBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


# ---------- Enrollment ----------

class EnrollmentBase(BaseModel):
    student_id: int
    course_id: int
    grade: Optional[str] = Field(None, max_length=2)


class EnrollmentCreate(EnrollmentBase):
    pass


class EnrollmentUpdate(BaseModel):
    grade: Optional[str] = Field(None, max_length=2)


class EnrollmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    student_id: int
    course_id: int
    enrolled_on: Optional[date] = None
    grade: Optional[str] = None


class EnrollmentWithCourse(EnrollmentOut):
    course: Optional[CourseOut] = None


class EnrollmentWithStudent(EnrollmentOut):
    student: Optional[StudentOut] = None


# ---------- Nested "detail" views that use the relationship ----------

class StudentWithCourses(StudentOut):
    enrollments: List[EnrollmentWithCourse] = []


class CourseWithStudents(CourseOut):
    enrollments: List[EnrollmentWithStudent] = []
