from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
<<<<<<< HEAD
from fastapi.staticfiles import StaticFiles
from fastapi_sqlalchemy import DBSessionMiddleware
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError
from contextlib import asynccontextmanager
import logging

=======
>>>>>>> 6026ab5 (ahmed alzain m1)
from config.database import Base, engine
from config.settings import settings
from app.routers.auth import router as auth_router
from app.routers.twofa import router as twofa_router
from app.routers.oauth_google import router as google_router

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

# Database setup
engine = create_engine(settings.DATABASE_URL, echo=True)
app.add_middleware(DBSessionMiddleware, custom_engine=engine)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

@app.get("/")
def read_root():
    return {"message": "Welcome to Syria GPT!", "docs": "/docs"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "Syria GPT Authentication API"}

@app.get("/hello/{name}")
def say_hello(name: str):
    return {"message": f"Hello, {name}! Welcome to Syria GPT."}

# Routers
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(twofa_router, prefix="/auth/2fa", tags=["2fa"])
app.include_router(google_router, prefix="/auth/oauth", tags=["oauth"]) 
