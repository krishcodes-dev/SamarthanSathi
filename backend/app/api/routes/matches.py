from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.models.crisis import (
    CrisisRequest, Resource, DispatchLog, RequestStatus, AvailabilityStatus
)
from app.utils.logger import log_dispatch
from pydantic import BaseModel
import uuid

router = APIRouter()

class DispatchBody(BaseModel):
    quantity: int = 1

@router.post("/{request_id}/dispatch/{resource_id}")
async def dispatch_resource(
    request_id: str,
    resource_id: str,
    payload: DispatchBody = Body(default=DispatchBody(quantity=1)),
    db: AsyncSession = Depends(get_db)
):
    """
    Dispatch a resource to a crisis request.
    
    - Updates request status to 'dispatched' (or 'in_progress')
    - Updates resource availability
    - Creates dispatch log entry
    """
    
    # Validate UUIDs
    try:
        req_uuid = uuid.UUID(request_id)
        res_uuid = uuid.UUID(resource_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid UUID format")

    # Fetch request
    result = await db.execute(select(CrisisRequest).where(CrisisRequest.id == req_uuid))
    request = result.scalar_one_or_none()
    
    if not request:
        raise HTTPException(status_code=404, detail="Request not found")
    
    # Fetch resource
    result = await db.execute(select(Resource).where(Resource.id == res_uuid))
    resource = result.scalar_one_or_none()
    
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    
    # Update request
    request.updated_at = datetime.utcnow()
    # If request is new, mark as dispatched? 
    # Or 'in_progress' if partial? Logic: dispatched implies action taken.
    request.status = RequestStatus.DISPATCHED
    
    # Update resource availability
    dispatch_qty = payload.quantity
    
    # Allow over-dispatching? Or cap at available?
    # Logic: Dispatch what I CAN.
    actual_dispatched = min(dispatch_qty, resource.quantity_available)
    # If explicit quantity requested > available, maybe warn? 
    # For now, just deduct.
    
    resource.quantity_available = max(0, resource.quantity_available - dispatch_qty)
    
    if resource.quantity_available == 0:
        resource.availability_status = AvailabilityStatus.UNAVAILABLE
    else:
        resource.availability_status = AvailabilityStatus.DISPATCHED
    
    resource.last_updated = datetime.utcnow()
    
    # Create dispatch log
    dispatch_log = DispatchLog(
        request_id=request.id,
        resource_id=resource.id,
        dispatched_quantity=dispatch_qty,
        dispatched_at=datetime.utcnow(),
        notes=f"Dispatched via dashboard. Requested: {dispatch_qty}"
    )
    db.add(dispatch_log)
    
    await db.commit()
    await db.refresh(resource)
    
    # Audit trail
    log_dispatch(
        request_id=str(request.id),
        resource_id=str(resource.id),
        quantity=dispatch_qty
    )
    
    return {
        "status": "success",
        "request_id": str(request.id),
        "resource_id": str(resource.id),
        "dispatched_quantity": dispatch_qty,
        "remaining_capacity": resource.quantity_available,
        "request_status": request.status # Renamed to avoid key collision
    }

