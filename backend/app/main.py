from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .api.api import api_router
from .core.config import get_settings
from .models.base import Base
from .db.session import engine

settings = get_settings()

app = FastAPI(
    title="Laboratory Management System",
    description="API for Laboratory Management System with AI capabilities",
    version="1.0.0"
)

# Create database tables
Base.metadata.create_all(bind=engine)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    return {"message": "Laboratory Management System API"}

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}
