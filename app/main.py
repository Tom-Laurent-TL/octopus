from fastapi import FastAPI, Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
import logging

from app.db.database import engine, Base
from app.api.v1.router import api_router
from app.core.bootstrap import router as bootstrap_router

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address, default_limits=["100/minute"])


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    
    # Create database tables (use Alembic for migrations instead of manual migration system)
    # Run `alembic upgrade head` to apply database migrations
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Create FastAPI app
    app = FastAPI(
        title="Octopus Chat",
        description="A FastAPI application with chat conversations",
        version="0.1.0",
    )
    
    # Add rate limiter
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    
    # Include API router
    app.include_router(api_router, prefix="/api/v1")
    
    # Include bootstrap router (no prefix - at root level)
    app.include_router(bootstrap_router)
    
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
