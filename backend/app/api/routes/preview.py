from fastapi import APIRouter, status, HTTPException
import uuid

from app.schemas.crisis import (
    CrisisRequestCreate,
    RequestPreviewResponse,
)
from app.services.hybrid_extraction import extract_entities
from app.services.location import resolve_location
from app.services.validator import validate_crisis_message
from app.services import calculate_urgency

# Isolated router for preview endpoint
router = APIRouter(tags=["Crisis Requests"])

@router.post(
    "/requests/preview",
    response_model=RequestPreviewResponse,
    status_code=status.HTTP_200_OK,
    summary="Preview a crisis request",
    description="Analyze text without storing. Used for user confirmation."
)
async def preview_crisis_request(
    request_data: CrisisRequestCreate,
) -> RequestPreviewResponse:
    """
    Generate a preview of the crisis request analysis.
    
    **Process:**
    1. Validate
    2. Extract entities
    3. Calculate urgency
    4. Return analysis (no DB write)
    """
    raw_text = request_data.raw_text
    
    # 1. Validate
    is_valid, validation_errors = validate_crisis_message(raw_text)
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "Invalid crisis message", "reasons": validation_errors}
        )
    
    # 2. Extract
    extraction = extract_entities(raw_text)
    
    # 3. Resolve location
    if extraction.location:
        location_match = resolve_location(extraction.location)
        if location_match:
            extraction.latitude = location_match.lat
            extraction.longitude = location_match.lng
            extraction.location = location_match.value
            extraction.location_confidence = location_match.confidence
            
    # 4. Urgency
    urgency = calculate_urgency(raw_text, extraction)
    
    return RequestPreviewResponse(
        preview_id=str(uuid.uuid4()),  # Temporary ID for frontend correlation
        raw_text=raw_text,
        extraction=extraction,
        urgency_analysis=urgency,
        flags=extraction.flags or []
    )
