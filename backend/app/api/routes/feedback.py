from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import logging
from typing import Dict, Any

from app.core.database import get_db
from app.models.feedback import UserFeedback, DispatcherFeedback
from app.schemas.crisis import UserFeedbackSubmit, DispatcherFeedbackSubmit

# Set up logging
logger = logging.getLogger(__name__)

from app.utils.db_types import generate_uuid

router = APIRouter(prefix="/feedback", tags=["Feedback"])

@router.post(
    "/user",
    status_code=status.HTTP_201_CREATED,
    summary="Submit user confirmation/correction",
    description="Captures feedback on extraction accuracy from the reporter."
)
async def submit_user_feedback(
    feedback_data: UserFeedbackSubmit,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, bool]:
    """
    Submit user feedback.
    """
    try:
        # Cast UUID to string for SQLite compatibility
        entry = UserFeedback(
            id=generate_uuid(),
            request_id=str(feedback_data.request_id),
            is_correct=feedback_data.is_correct,
            corrected_text=feedback_data.corrected_text
        )
        db.add(entry)
        await db.commit()
        return {"success": True}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to save user feedback: {str(e)}")
        # Fail silent to frontend
        return {"success": False}

@router.post(
    "/dispatcher",
    status_code=status.HTTP_201_CREATED,
    summary="Submit dispatcher performance ratings",
    description="Captures detailed ratings on extraction and matching quality."
)
async def submit_dispatcher_feedback(
    feedback_data: DispatcherFeedbackSubmit,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, bool]:
    """
    Submit dispatcher feedback.
    """
    try:
        # Cast UUID to string for SQLite compatibility
        entry = DispatcherFeedback(
            id=generate_uuid(),
            request_id=str(feedback_data.request_id),
            extraction_rating=feedback_data.extraction_rating,
            matching_rating=feedback_data.matching_rating,
            comment=feedback_data.comment
        )
        db.add(entry)
        await db.commit()
        return {"success": True}
        
    except Exception as e:
        await db.rollback()
        logger.error(f"Failed to save dispatcher feedback: {str(e)}")
        # Fail silent to frontend
        return {"success": False}
