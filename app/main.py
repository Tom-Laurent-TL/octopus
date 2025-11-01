from fastapi import FastAPI

from app.core.config import settings
from app.db.database import engine, Base
from app.api.v1.router import api_router


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    # Create database tables
    Base.metadata.create_all(bind=engine)
    
    # Create FastAPI app
    app = FastAPI(
        title="FastAPI App",
        description="A FastAPI application with chat conversations",
        version="0.1.0",
    )
    
    # Include API router
    app.include_router(api_router, prefix="/api/v1")
    
    # Root endpoint
    @app.get("/")
    async def root():
        return {
            "message": "Hello! Visit /docs for API documentation",
            "version": "0.1.0"
        }
    
    @app.get("/health")
    async def health():
        return {"status": "healthy"}
    
    return app


app = create_app()
