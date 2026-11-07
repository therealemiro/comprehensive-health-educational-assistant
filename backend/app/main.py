"""
main.py

Main entry point for the FastAPI application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler

from app.database import Base, engine
from app import models  # noqa: F401 -- Required for SQLAlchemy to recognize the models.
from app.auth.routes import router as auth_router
from app.chats.routes import router as chats_router
from app.limiter import limiter


# During development, create database tables directly from the models.
# For production, a migration tool such as Alembic is recommended.
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Comprehensive Health Educational Assistant - API",
    description="Final project backend: RAG-based educational chatbot for health and medication information.",
    version="0.1.0",
)


# Register the rate limiter to prevent brute-force attacks on /auth/login.
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Allow requests from the frontend, which runs on a different port.
# During development, common Vite/React ports are allowed.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(chats_router)


@app.get("/health", tags=["System"])
def health_check():
    """Simple endpoint for checking whether the server is running and accessible."""
    return {"status": "ok"}