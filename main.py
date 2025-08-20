from fastapi import FastAPI
from fastapi_sqlalchemy import DBSessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
import logging

from config.model import Base
from config.settings import settings
from routes.auth import router as auth_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Syria GPT API",
    description="Authentication API for Syria GPT with Google OAuth 2.0 integration",
    version="1.0.0"
)

engine = create_engine(settings.DATABASE_URL, echo=True)

app.add_middleware(DBSessionMiddleware, custom_engine=engine)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)

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
