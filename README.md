# Student Record System API

A backend for managing students, courses, and enrollments — built for the
Tech4Girls Backend Development Cohort 5 final project (Option C: full stack).

A registrar's office can keep a list of **students**, a catalogue of
**courses**, and record which students are **enrolled** in which courses
— including the grade each student earned. A small vanilla HTML/CSS/JS
frontend is included so you can browse and manage everything without
needing Postman.

## What it does

- **Students** — name, email, date of birth, phone.
- **Courses** — code (e.g. "ICT 314"), title, description, credit value.
- **Enrollments** — the link between a student and a course. A student can
  be enrolled in many courses, and a course can have many students
  enrolled — a genuine **many-to-many** relationship. The enrollment
  itself also stores the date the student enrolled and the grade they
  earned, so it's modelled as its own table rather than a bare join
  table.

## Tech stack

- **FastAPI** — web framework
- **SQLAlchemy** — ORM (no raw SQL)
- **MySQL** — database, connected via `PyMySQL`
- **python-dotenv** — loads DB credentials from `.env`
- **Vanilla HTML/CSS/JS** — simple frontend, no build step

## Project structure

```
t4g-cohort5-final-project/
├── app/
│   ├── main.py                     # FastAPI app, CORS, error handling
│   ├── database.py                 # SQLAlchemy engine/session setup
│   ├── models.py                   # ORM models (Student, Course, Enrollment)
│   ├── schemas.py                  # Pydantic request/response schemas
│   ├── repositories/                # DB queries, kept out of route handlers
│   │   ├── student_repository.py
│   │   ├── course_repository.py
│   │   └── enrollment_repository.py
│   └── routers/                     # API route handlers
│       ├── students.py
│       ├── courses.py
│       └── enrollments.py
├── frontend/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Setup

### 1. Prerequisites

- Python 3.10+
- A running MySQL server (locally, or via something like XAMPP/MySQL
  Workbench/Docker)

### 2. Create the database

Log into MySQL and create an empty database:

```sql
CREATE DATABASE student_records_db;
```

The tables themselves are created automatically the first time you run
the app — you don't need to write any `CREATE TABLE` statements.

### 3. Clone and set up a virtual environment

```bash
git clone https://github.com/<your-username>/t4g-cohort5-final-project.git
cd t4g-cohort5-final-project

python -m venv venv
source venv/bin/activate        # on Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example file and fill in your own MySQL credentials:

```bash
cp .env.example .env
```

Edit `.env`:

```
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
DB_NAME=student_records_db
```

`.env` is already listed in `.gitignore`, so your credentials never get
committed.

### 5. Run the API

```bash
uvicorn app.main:app --reload
```

The API will be running at `http://127.0.0.1:8000`.

Interactive docs (Swagger UI) are available at
`http://127.0.0.1:8000/docs` — the fastest way to try every endpoint
without writing any code.

### 6. Run the frontend

The frontend is plain HTML/CSS/JS, so no build step is needed. Just open
`frontend/index.html` directly in your browser (double-click it, or use
the VS Code "Live Server" extension). It talks to the API at
`http://127.0.0.1:8000` — make sure the backend from step 5 is running
first.

## API Reference

### Students

| Method | Endpoint             | Description                                  |
|--------|------------------------|------------------------------------------------|
| POST   | `/students`           | Create a student                               |
| GET    | `/students`           | List all students                              |
| GET    | `/students/{id}`      | Get one student with their enrolled courses    |
| PUT    | `/students/{id}`      | Update a student                               |
| DELETE | `/students/{id}`      | Delete a student (and their enrollments)       |

### Courses

| Method | Endpoint             | Description                                  |
|--------|------------------------|------------------------------------------------|
| POST   | `/courses`             | Create a course                                |
| GET    | `/courses`             | List all courses                               |
| GET    | `/courses/{id}`        | Get one course with its enrolled students      |
| PUT    | `/courses/{id}`        | Update a course                                |
| DELETE | `/courses/{id}`        | Delete a course (and its enrollments)          |

### Enrollments

| Method | Endpoint                                         | Description                                   |
|--------|-----------------------------------------------------|--------------------------------------------------|
| POST   | `/enrollments`                                      | Enrol a student in a course                       |
| GET    | `/enrollments` (`?student_id=` / `?course_id=`)     | List enrollments, optionally filtered             |
| GET    | `/enrollments/{id}`                                 | Get one enrollment                                |
| PUT    | `/enrollments/{id}`                                 | Update an enrollment (mainly used to set a grade) |
| DELETE | `/enrollments/{id}`                                 | Unenrol a student from a course                   |

## Example request

Create a student:

```bash
curl -X POST http://127.0.0.1:8000/students \
  -H "Content-Type: application/json" \
  -d '{"first_name": "Ama", "last_name": "Owusu", "email": "ama@example.com"}'
```

Create a course:

```bash
curl -X POST http://127.0.0.1:8000/courses \
  -H "Content-Type: application/json" \
  -d '{"code": "ICT 314", "title": "Software Engineering", "credits": 3}'
```

Enrol the student in the course:

```bash
curl -X POST http://127.0.0.1:8000/enrollments \
  -H "Content-Type: application/json" \
  -d '{"student_id": 1, "course_id": 1}'
```

## Error handling

- Missing records return **404** with a clear message.
- Invalid input (e.g. enrolling a student in a course that doesn't exist,
  a duplicate email, a duplicate course code, or enrolling the same
  student in the same course twice) returns **400**.
- Validation errors (e.g. missing required fields, a malformed email,
  wrong data types) return **422**, handled automatically by
  FastAPI/Pydantic.
- Unexpected database errors are caught and return a clean **500**
  instead of crashing the server or leaking a stack trace.

## Notes on design decisions

- **Repository layer**: all database queries live in `app/repositories/`,
  never directly in the route handlers. This keeps `routers/` focused on
  HTTP concerns (status codes, validation) and makes the query logic easy
  to test or reuse.
- **Enrollment as its own model**: a plain many-to-many association table
  would only be able to say *that* a student and a course are linked. By
  giving `Enrollment` its own primary key, `enrolled_on` date, and
  `grade` column, it can also say *how* — which is what a real registrar
  system needs.
- **Cascade deletes**: deleting a student removes their enrollments;
  deleting a course removes its enrollments too. The database never ends
  up with orphaned rows pointing at something that no longer exists.
- **Uniqueness rules**: a student can't be enrolled in the same course
  twice (enforced both at the database level with a unique constraint,
  and checked explicitly in the API so it returns a clean 400 instead of
  a raw database error).
- **Separate Pydantic schemas** for create/update/output mean the API
  never accidentally exposes internal fields, and `Update` schemas make
  every field optional so partial updates (`PUT`) work naturally.
