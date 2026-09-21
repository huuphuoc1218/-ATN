from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.core.database import engine, Base
from app.api.api import api_router
from app.api.endpoints import webhooks
from app.core.storage import ensure_uploads_root

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Pickleball NP SPORTCLUB API",
    description="Backend API for Pickleball booking system",
    version="1.0.0",
    debug=settings.DEBUG
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api")

# Include webhooks router (no auth required)
app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])

# Mount static files for uploads
uploads_dir = ensure_uploads_root()
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")


@app.get("/")
def root():
    return {
        "message": "Welcome to Pickleball NP SPORTCLUB API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    return {"status": "healthy"}