"""
API routes for crisis request management.

Thin layer that wires business logic services to HTTP endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
import uuid

from app.core.database import get_db
from app.models.crisis import CrisisRequest, Resource, DispatchLog, RequestStatus, ResourceType
from app.schemas.crisis import (
    CrisisRequestCreate,
    CrisisRequestResponse,
    CrisisRequestQueueItem,
    ResourceMatchResponse,
    DispatchResponse,
)
from app.services import (
    is_valid_crisis_request,
    extract_entities,
    calculate_urgency,
    match_crisis_request,
)
from app.services.hybrid_extraction import extract_entities
from app.services.location import resolve_location
from app.services.validator import validate_crisis_message
from app.utils.logger import log_request_processing


router = APIRouter(prefix="/requests", tags=["Crisis Requests"])


@router.post(
    "/submit",
    response_model=CrisisRequestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a new crisis request",
    description="Validates, extracts entities, scores urgency, and stores a crisis request"
)
async def submit_crisis_request(
    request_data: CrisisRequestCreate,
    db: AsyncSession = Depends(get_db)
) -> CrisisRequestResponse:
    """
    Submit a new crisis request for processing.
    
    **Process:**
    1. Validate message (spam filtering, crisis indicators)
    2. Extract entities (need type, location, quantity, contact)
    3. Resolve location to coordinates
    4. Calculate urgency score (U1-U5)
    5. Store in database with structured outputs
    
    **Returns:** Complete crisis request with extraction and urgency analysis
    """
    raw_text = request_data.raw_text
    
    # 1. Validate
    is_valid, validation_errors = validate_crisis_message(raw_text)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "Invalid crisis message",
                "reasons": validation_errors
            }
        )
    
    # 2. Extract entities
    extraction = extract_entities(raw_text)
    
    # 3. Resolve location (if extracted)
    if extraction.location:
        location_match = resolve_location(extraction.location)
        if location_match:
            extraction.latitude = location_match.lat
            extraction.longitude = location_match.lng
            extraction.location = location_match.value  # Use resolved canonical name
            extraction.location_confidence = location_match.confidence
    
    # 4. Calculate urgency
    urgency = calculate_urgency(raw_text, extraction)
    
    # 5. Store in database
    crisis_request = CrisisRequest(
        id=uuid.uuid4(),
        raw_text=raw_text,
        extraction=extraction.model_dump(exclude_none=True),
        urgency_analysis=urgency.model_dump(exclude_none=True),
        status=RequestStatus.NEW
    )
    
    db.add(crisis_request)
    await db.commit()
    await db.refresh(crisis_request)
    
    # Audit Logging
    log_request_processing(
        request_id=str(crisis_request.id),
        raw_message=raw_text,
        extraction_result=extraction.model_dump(),
        urgency_result=urgency.model_dump()
    )
    
    return CrisisRequestResponse.model_validate(crisis_request)


@router.get(
    "/queue",
    response_model=List[CrisisRequestQueueItem],
    summary="Get crisis request queue",
    description="Retrieve all pending/in-progress requests, sorted by urgency"
)
async def get_crisis_queue(
    db: AsyncSession = Depends(get_db),
    status_filter: RequestStatus = None,
    limit: int = 50
) -> List[CrisisRequestQueueItem]:
    """
    Get queue of crisis requests.
    
    **Sort order:** Urgency score (descending), then created_at (ascending)
    
    **Query params:**
    - status_filter: Optional filter by status (NEW, IN_PROGRESS, etc.)
    - limit: Max results (default: 50)
    """
    query = select(CrisisRequest)
    
    # Filter by status if provided
    if status_filter:
        query = query.where(CrisisRequest.status == status_filter)
    else:
        # Default: only active requests
        query = query.where(
            CrisisRequest.status.in_([RequestStatus.NEW, RequestStatus.IN_PROGRESS])
        )
    
    # Sort by urgency score (database-agnostic approach)
    # For production PostgreSQL: Use (urgency_analysis->>'score')::int
    # For SQLite: Use json_extract(urgency_analysis, '$.score')
    from sqlalchemy import func, cast, Integer
    
    # Use JSON extraction that works across databases
    try:
        # Try PostgreSQL JSONB syntax first (production)
        from sqlalchemy import text, desc
        query = query.order_by(
            desc(text("CAST(json_extract(urgency_analysis, '$.score') AS INTEGER)")),
            CrisisRequest.created_at.asc()
        ).limit(limit)
    except Exception:
        # Fallback to Python sorting if database doesn't support JSON functions
        query = query.limit(limit)
    
    result = await db.execute(query)
    requests = result.scalars().all()
    
    # If we couldn't sort in SQL, sort in Python as fallback
    if 'json_extract' not in str(query):
        requests = sorted(
            requests,
            key=lambda r: r.urgency_analysis.get('score', 0) if r.urgency_analysis else 0,
            reverse=True
        )
    
    return [CrisisRequestQueueItem.model_validate(r) for r in requests]


@router.get(
    "/{request_id}",
    response_model=CrisisRequestResponse,
    summary="Get crisis request by ID",
    description="Retrieve a specific crisis request with all analysis"
)
async def get_crisis_request(
    request_id: uuid.UUID,
    db: AsyncSession = Depends(get_db)
) -> CrisisRequestResponse:
    """
    Retrieve a specific crisis request by ID.
    
    **Returns:** Complete crisis request with extraction and urgency data
    """
    result = await db.execute(
        select(CrisisRequest).where(CrisisRequest.id == request_id)
    )
    crisis_request = result.scalar_one_or_none()
    
    if not crisis_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crisis request {request_id} not found"
        )
    
    return CrisisRequestResponse.model_validate(crisis_request)


@router.get(
    "/{request_id}/matches",
    response_model=List[ResourceMatchResponse],
    summary="Get resource matches for a request",
    description="Find top matching resources for a crisis request"
)
async def get_resource_matches(
    request_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    top_n: int = 3
) -> List[ResourceMatchResponse]:
    """
    Get matched resources for a crisis request.
    
    **Matching algorithm:**
    - Urgency-aware distance weighting
    - Quantity match scoring
    - Partial fulfillment detection
    
    **Query params:**
    - top_n: Number of matches to return (default: 3)
    """
    # 1. Get crisis request
    result = await db.execute(
        select(CrisisRequest).where(CrisisRequest.id == request_id)
    )
    crisis_request = result.scalar_one_or_none()
    
    if not crisis_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crisis request {request_id} not found"
        )
    
    # 2. Validate extraction has required fields
    if not crisis_request.extraction:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request has no entity extraction data"
        )
    
    extraction = crisis_request.extraction
    if not all(k in extraction for k in ['latitude', 'longitude', 'need_type']):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Request missing required fields (latitude, longitude, need_type)"
        )
    
    # 3. Get available resources
    try:
        resource_type_enum = ResourceType(extraction['need_type'])
    except ValueError:
        # Try case-insensitive match if direct lookup fails
        try:
            resource_type_enum = ResourceType(extraction['need_type'].upper())
        except ValueError:
            return []

    resource_result = await db.execute(
        select(Resource).where(
            Resource.resource_type == resource_type_enum
        )
    )
    available_resources = resource_result.scalars().all()
    
    if not available_resources:
        return []  # No resources of this type
    
    # 4. Build matching request dict
    urgency_analysis = crisis_request.urgency_analysis or {}
    matching_request = {
        'latitude': extraction['latitude'],
        'longitude': extraction['longitude'],
        'need_type': extraction['need_type'],
        'quantity': extraction.get('quantity'),
        'urgency_score': urgency_analysis.get('score', 0),
        'urgency_level': urgency_analysis.get('level', 'U4')
    }
    
    # 5. Run matching algorithm
    matches = match_crisis_request(
        crisis_request=matching_request,
        available_resources=available_resources,
        top_n=top_n
    )
    
    # 6. Convert to response model
    return [
        ResourceMatchResponse(
            resource_id=m['resource_id'],
            provider_name=m['provider_name'],
            resource_type=m['resource_type'],
            quantity_available=m['quantity_available'],
            location_name=m['location_name'],
            distance_km=m['distance_km'],
            match_score=m['match_score'],
            is_partial_fulfillment=m['is_partial_fulfillment'],
            fulfillment_ratio=m['fulfillment_ratio'],
            reasoning=m['reasoning']
        )
        for m in matches
    ]


@router.post(
    "/{request_id}/dispatch/{resource_id}",
    response_model=DispatchResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Dispatch a resource to a request",
    description="Create a dispatch log and update request/resource statuses"
)
async def dispatch_resource(
    request_id: uuid.UUID,
    resource_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
    quantity: int = None,
    notes: str = None
) -> DispatchResponse:
    """
    Dispatch a resource to a crisis request.
    
    **Process:**
    1. Validate request and resource exist
    2. Create dispatch log
    3. Update request status to IN_PROGRESS/RESOLVED
    4. Decrement resource quantity
    
    **Query params:**
    - quantity: Amount to dispatch (defaults to request quantity or 1)
    - notes: Optional dispatch notes
    """
    # 1. Get crisis request
    request_result = await db.execute(
        select(CrisisRequest).where(CrisisRequest.id == request_id)
    )
    crisis_request = request_result.scalar_one_or_none()
    
    if not crisis_request:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Crisis request {request_id} not found"
        )
    
    
    # 2. Determine dispatch quantity
    if quantity is None:
        extraction = crisis_request.extraction or {}
        quantity = extraction.get('quantity', 1)
    
    # 3. Get resource with row-level lock to prevent race conditions
    resource_result = await db.execute(
        select(Resource)
        .where(Resource.id == resource_id)
        .where(Resource.quantity_available >= quantity)  # Pre-check quantity
        .with_for_update()  # Lock row until transaction commits
    )
    resource = resource_result.scalar_one_or_none()
    
    if not resource:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Resource unavailable or insufficient quantity. Available quantity may have changed."
        )
    
    # 4. Final validation (defensive check)
    if resource.quantity_available < quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Insufficient quantity. Available: {resource.quantity_available}, requested: {quantity}"
        )
    
    # 5. Create dispatch log
    dispatch_log = DispatchLog(
        id=uuid.uuid4(),
        request_id=request_id,
        resource_id=resource_id,
        dispatched_quantity=quantity,
        notes=notes
    )
    
    # 6. Update resource quantity
    resource.quantity_available -= quantity
    
    # 7. Update request status
    if crisis_request.status == RequestStatus.NEW:
        crisis_request.status = RequestStatus.IN_PROGRESS
    
    # Commit all changes
    db.add(dispatch_log)
    await db.commit()
    await db.refresh(dispatch_log)
    
    return DispatchResponse(
        dispatch_id=dispatch_log.id,
        request_id=request_id,
        resource_id=resource_id,
        quantity_dispatched=quantity,
        resource_provider=resource.provider_name,
        dispatched_at=dispatch_log.dispatched_at,
        notes=notes,
        message=f"Dispatched {quantity} units from {resource.provider_name}"
    )
