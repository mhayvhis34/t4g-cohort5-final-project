"""
Student Record System API
--------------------------
A backend for managing students, courses, and enrollments (the many-to-many
link between them, which also carries a grade and enrollment date).

Run with:
    uvicorn app.main:app --reload
"""

from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from sqlalchemy.exc import SQLAlchemyError

from app.database import Base, engine
from app.routers import students, courses, enrollments

# Creates tables if they don't already exist (does not alter existing ones)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Student Record System API",
    description="Manage students, courses, and course enrollments.",
    version="1.0.0",
)

# Allow the simple frontend (served from anywhere/file://) to call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(SQLAlchemyError)
async def db_exception_handler(request: Request, exc: SQLAlchemyError):
    """
    Catch-all so a database hiccup returns a clean JSON 500 instead of
    crashing the server or leaking a stack trace to the client.
    """
    return JSONResponse(
        status_code=500,
        content={"detail": "A database error occurred. Please try again."},
    )


app.include_router(students.router)
app.include_router(courses.router)
app.include_router(enrollments.router)

# Serve frontend files
frontend_path = Path(__file__).parent.parent / "frontend"


@app.get("/", tags=["Frontend"])
async def serve_index():
    """Serve the frontend HTML at the root."""
    index_file = frontend_path / "index.html"
    if index_file.exists():
        return FileResponse(index_file, media_type="text/html")
    return {"error": "Frontend not found"}


@app.get("/style.css", tags=["Frontend"])
async def serve_style():
    """Serve the CSS stylesheet."""
    style_file = frontend_path / "style.css"
    if style_file.exists():
        return FileResponse(style_file, media_type="text/css")
    return {"error": "Style not found"}


@app.get("/app.js", tags=["Frontend"])
async def serve_app_js():
    """Serve the JavaScript app."""
    js_file = frontend_path / "app.js"
    if js_file.exists():
        return FileResponse(js_file, media_type="application/javascript")
    return {"error": "App JS not found"}


@app.get("/health", tags=["Root"])
def health_check():
    return {"status": "ok"}
