"""
Main FastAPI application for CJEI Board Game Recommendation System.
"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings

# Import models first to ensure proper relationship resolution
from .models import recommendation, game, session, skill  # noqa: F401

from .games.router import router as games_router
from .sessions.router import router as sessions_router
from .skills.router import router as skills_router
from .recommendations.router import router as recommendations_router
from .feedback.router import router as feedback_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Sistema de recomendación de juegos de mesa para asesores pedagógicos del CJEI",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(games_router, prefix=settings.API_PREFIX)
app.include_router(sessions_router, prefix=settings.API_PREFIX)
app.include_router(skills_router, prefix=settings.API_PREFIX)
app.include_router(recommendations_router, prefix=settings.API_PREFIX)
app.include_router(feedback_router, prefix=settings.API_PREFIX)


@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "message": "CJEI Board Game Recommendation System API",
        "version": settings.VERSION,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "version": settings.VERSION}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
