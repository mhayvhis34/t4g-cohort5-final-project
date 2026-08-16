"""
SQLAlchemy ORM models.

Relationship:
- Student (many) <-> Course (many), linked through Enrollment.
  Enrollment is modelled as its own table (not a bare association table)
  because it carries its own data: the date a student enrolled and the
  grade they earned. This is the standard pattern for a many-to-many
  relationship that needs extra fields on the "join".
"""

from sqlalchemy import Column, Integer, String, Date, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(80), nullable=False)
    last_name = Column(String(80), nullable=False)
    email = Column(String(150), nullable=False, unique=True, index=True)
    date_of_birth = Column(Date, nullable=True)
    phone = Column(String(30), nullable=True)

    enrollments = relationship(
        "Enrollment", back_populates="student", cascade="all, delete-orphan"
    )


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(20), nullable=False, unique=True)  # e.g. "ICT 314"
    title = Column(String(150), nullable=False)
    description = Column(String(500), nullable=True)
    credits = Column(Integer, nullable=False, default=3)

    enrollments = relationship(
        "Enrollment", back_populates="course", cascade="all, delete-orphan"
    )


class Enrollment(Base):
    """
    The join between a Student and a Course.
    A student can only be enrolled in the same course once
    (enforced by the unique constraint below).
    """

    __tablename__ = "enrollments"
    __table_args__ = (
        UniqueConstraint("student_id", "course_id", name="uq_student_course"),
    )

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    enrolled_on = Column(Date, server_default=func.current_date())
    grade = Column(String(2), nullable=True)  # e.g. "A", "B+", null until graded

    student = relationship("Student", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")
