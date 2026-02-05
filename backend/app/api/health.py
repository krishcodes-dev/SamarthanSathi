"""
Health check endpoint with dependency validation.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.services.extraction import nlp

router = APIRouter()


@router.get("/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint with dependency validation.
    
    Returns:
        Health status including SpaCy and database connectivity
        
    Raises:
        503 Service Unavailable if any critical dependency is down
    """
    status = {
        "status": "healthy",
        "dependencies": {
            "spacy": "unknown",
            "database": "unknown"
        }
    }
    
    # Check SpaCy model
    if nlp is not None:
        status["dependencies"]["spacy"] = "loaded"
    else:
        status["dependencies"]["spacy"] = "missing"
        status["status"] = "unhealthy"
    
    # Check database connection
    try:
        await db.execute(text("SELECT 1"))
        status["dependencies"]["database"] = "connected"
    except Exception as e:
        status["dependencies"]["database"] = f"error: {str(e)}"
        status["status"] = "unhealthy"
    
    # Return 503 if unhealthy
    if status["status"] != "healthy":
        raise HTTPException(status_code=503, detail=status)
    
    return status
