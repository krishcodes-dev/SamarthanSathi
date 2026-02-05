"""
FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.database import init_db
from app.api.health import router as health_router
from app.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan events.
    Handles startup and shutdown logic.
    """
    # Startup
    print(f"🚀 Starting {settings.APP_NAME} in {settings.ENV} mode...")
    
    # Validate SpaCy model loaded (fail fast if missing)
    from app.services.extraction import nlp
    if nlp is None:
        raise RuntimeError(
            "❌ SpaCy model 'en_core_web_md' not loaded!\n"
            "   Run: python -m spacy download en_core_web_md"
        )
    print("✅ SpaCy NLP model loaded")
    
    # Initialize database
    await init_db()
    print("✅ Database initialized")
    
    # Validate database connection
    from sqlalchemy import text
    from app.core.database import engine
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        print("✅ Database connection verified")
    except Exception as e:
        raise RuntimeError(f"❌ Database connection failed: {e}")
    
    yield
    
    # Shutdown
    print("👋 Shutting down...")
    await engine.dispose()


# Create FastAPI application
app = FastAPI(
    title=settings.APP_NAME,
    description="Crisis Need to Resource Matching Engine",
    version="0.1.0",
    lifespan=lifespan,
    debug=settings.DEBUG,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(health_router, tags=["Health"])
app.include_router(api_router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": f"Welcome to {settings.APP_NAME} API",
        "docs": "/docs",
        "health": "/health"
    }
