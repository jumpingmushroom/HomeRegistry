from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from .database import init_db
from .config import settings, cors_origins
from .api import settings as settings_api
from .api import locations, categories, items, images, documents, dashboard, init


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    init_db()
    yield


# Create FastAPI app
app = FastAPI(
    title="HomeRegistry API",
    description="Home Inventory Management System with AI-powered photo analysis",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(settings_api.router)
app.include_router(locations.router)
app.include_router(categories.router)
app.include_router(items.router)
app.include_router(images.router)
app.include_router(documents.router)
app.include_router(dashboard.router)
app.include_router(init.router)


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "version": "1.0.0"}


# Serve frontend static files (for production)
# This will be mounted after building the frontend
try:
    app.mount("/", StaticFiles(directory="/app/frontend/dist", html=True), name="static")
except RuntimeError:
    # Frontend not built yet, skip mounting
    pass


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.backend_host,
        port=settings.backend_port,
        reload=False
    )
