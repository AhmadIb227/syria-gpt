"""Main FastAPI application with Clean Architecture."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager

from config.database import init_db
from config.settings import settings
from config.logging_config import setup_logging
from config.exceptions import (
    SyriaGPTException,
    syria_gpt_exception_handler,
    validation_exception_handler,
    database_exception_handler,
    general_exception_handler,
)
from presentation.api import auth_router

# Setup logging
logger = setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management."""
    # Startup
    logger.info("Starting Syria GPT API...")
    yield
    # Shutdown
    logger.info("Shutting down Syria GPT API...")

def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Syria GPT API",
        description="Clean Architecture Authentication API with OAuth 2.0 integration",
        version="2.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.DEBUG else None,
        redoc_url="/redoc" if settings.DEBUG else None,
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        allow_headers=["*"],
    )

    # Add exception handlers
    app.add_exception_handler(SyriaGPTException, syria_gpt_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(SQLAlchemyError, database_exception_handler)
    app.add_exception_handler(Exception, general_exception_handler)

    # Include routers
    app.include_router(auth_router)

    # Health endpoints
    @app.get("/")
    def read_root():
        """Root endpoint."""
        return {
            "message": "Welcome to Syria GPT Clean Architecture API!",
            "version": "2.0.0",
            "docs": "/docs" if settings.DEBUG else "Contact admin for API documentation",
        }

    @app.get("/health")
    def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "service": "Syria GPT Clean Architecture API", "version": "2.0.0"}

    return app

app = create_app()