from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Board Game Recommendations System API",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

# TODO: Include routers for different API endpoints
# from app.api import auth, games, recommendations, users
# app.include_router(auth.router, prefix=f"{settings.API_V1_PREFIX}/auth", tags=["auth"])
# app.include_router(games.router, prefix=f"{settings.API_V1_PREFIX}/games", tags=["games"])
# app.include_router(recommendations.router, prefix=f"{settings.API_V1_PREFIX}/recommendations", tags=["recommendations"])
# app.include_router(users.router, prefix=f"{settings.API_V1_PREFIX}/users", tags=["users"])
