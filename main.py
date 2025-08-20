from fastapi import FastAPI, HTTPException
from fastapi_sqlalchemy import DBSessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager
import logging

from config.model import Base
from config.settings import settings
from config.logging_config import setup_logging
from config.exceptions import (
    SyriaGPTException,
    syria_gpt_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    database_exception_handler,
    general_exception_handler,
)
from routes.auth import router as auth_router

# Setup logging
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    try:
        logger.info("Starting Syria GPT API...")
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        logger.info("Syria GPT API started successfully")
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Syria GPT API...")

app = FastAPI(
    title="Syria GPT API",
    description="Authentication API for Syria GPT with Google OAuth 2.0 integration",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

engine = create_engine(settings.DATABASE_URL, echo=True)

app.add_middleware(DBSessionMiddleware, custom_engine=engine)

# Configure CORS with environment-based origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Add exception handlers
app.add_exception_handler(SyriaGPTException, syria_gpt_exception_handler)
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(SQLAlchemyError, database_exception_handler)
app.add_exception_handler(Exception, general_exception_handler)

# Include routers
app.include_router(auth_router, prefix="/auth", tags=["authentication"])


@app.get("/")
def read_root():
    return {"message": "Welcome to Syria GPT!", "docs": "/docs"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Syria GPT Authentication API"}

@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Hello, {name}! Welcome to Syria GPT."}
