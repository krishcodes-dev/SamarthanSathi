"""
Pydantic schemas for SamarthanSathi crisis-response system.

These schemas define the API contract for request/response validation.
"""
from datetime import datetime
from typing import Optional, List
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict

from app.models.crisis import RequestStatus, ResourceType, AvailabilityStatus


# ===== ENTITY EXTRACTION SCHEMAS =====

class EntityExtraction(BaseModel):
    """
    Output schema for entity extraction from crisis text.
    
    Represents the structured information extracted from raw crisis messages.
    """
    model_config = ConfigDict(from_attributes=True)
    
    need_type: Optional[str] = Field(
        None,
        description="Type of need (medical, food, water, shelter, etc.)",
        examples=["medical", "food"]
    )
    need_type_confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Confidence score for need type extraction"
    )
    
    quantity: Optional[int] = Field(
        None,
        description="Quantity requested (number of units/people)",
        examples=[50, 100]
    )
    quantity_confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Confidence score for quantity extraction"
    )
    
    location: Optional[str] = Field(
        None,
        description="Extracted location name",
        examples=["Andheri East", "Near Malad Station"]
    )
    location_confidence: Optional[float] = Field(
        None,
        ge=0.0,
        le=1.0,
        description="Confidence score for location extraction"
    )
    location_alternatives: Optional[list[str]] = Field(
        None,
        description="Alternative location matches if ambiguous"
    )
    
    latitude: Optional[float] = Field(
        None,
        ge=-90.0,
        le=90.0,
        description="Resolved GPS latitude"
    )
    longitude: Optional[float] = Field(
        None,
        ge=-180.0,
        le=180.0,
        description="Resolved GPS longitude"
    )
    
    contact: Optional[str] = Field(
        None,
        description="Extracted contact phone number",
        examples=["+919876543210"]
    )
    
    affected_count: Optional[str] = Field(
        None,
        description="Number of people affected (may be text like 'multiple')",
        examples=["50", "multiple", "unknown"]
    )


class UrgencyAnalysis(BaseModel):
    """
    Output schema for urgency scoring analysis.
    
    Provides urgency score, level, and explainability.
    """
    model_config = ConfigDict(from_attributes=True)
    
    score: int = Field(
        ...,
        ge=0,
        le=100,
        description="Urgency score (0-100)",
        examples=[95, 60, 20]
    )
    
    level: str = Field(
        ...,
        description="Urgency level classification",
        examples=["U1 - Critical", "U2 - Urgent", "U3 - Moderate"]
    )
    
    reasoning: list[str] = Field(
        ...,
        description="Itemized reasoning for urgency score",
        examples=[
            ["Life-threatening keywords detected (+50)", "Critical need type: rescue (+30)"]
        ]
    )
    
    confidence: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Confidence in urgency assessment",
        examples=[0.92]
    )
    
    flags: Optional[list[str]] = Field(
        None,
        description="Warning flags or missing information",
        examples=[["Missing contact information"]]
    )


# ===== CRISIS REQUEST SCHEMAS =====

class CrisisRequestCreate(BaseModel):
    """Schema for creating a new crisis request."""
    model_config = ConfigDict(from_attributes=True)
    
    raw_text: str = Field(
        ...,
        min_length=10,
        max_length=5000,
        description="Raw crisis message text",
        examples=["Need 50 blankets urgently near Andheri station. 20 families affected. Contact: 9876543210"]
    )


class CrisisRequestResponse(BaseModel):
    """Schema for crisis request API response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    raw_text: str
    created_at: datetime
    updated_at: datetime
    status: RequestStatus
    
    extraction: Optional[EntityExtraction] = None
    urgency_analysis: Optional[UrgencyAnalysis] = None


class CrisisRequestQueueItem(BaseModel):
    """Schema for crisis request in queue listing."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    raw_text: str
    created_at: datetime
    status: RequestStatus
    urgency_score: Optional[int] = Field(None, description="Urgency score 0-100")
    urgency_level: Optional[str] = Field(None, description="Urgency level (U1-U5)")
    need_type: Optional[str] = Field(None, description="Type of need")
    location: Optional[str] = Field(None, description="Location string")
    
    @classmethod
    def model_validate(cls, obj):
        """Custom validation to extract nested fields."""
        data = {
            'id': obj.id,
            'raw_text': obj.raw_text,
            'created_at': obj.created_at,
            'status': obj.status,
        }
        
        # Extract from urgency_analysis
        if obj.urgency_analysis:
            data['urgency_score'] = obj.urgency_analysis.get('score')
            data['urgency_level'] = obj.urgency_analysis.get('level')
        
        # Extract from extraction
        if obj.extraction:
            data['need_type'] = obj.extraction.get('need_type')
            data['location'] = obj.extraction.get('location')
        
        return cls(**data)


class ResourceMatchResponse(BaseModel):
    """Schema for resource match result."""
    resource_id: UUID
    provider_name: str
    resource_type: str
    quantity_available: int
    location_name: str
    distance_km: float
    match_score: float = Field(..., ge=0.0, le=1.0, description="Match score 0-1")
    is_partial_fulfillment: bool
    fulfillment_ratio: float = Field(..., ge=0.0, le=1.0)
    reasoning: List[str]


class DispatchResponse(BaseModel):
    """Schema for dispatch operation response."""
    dispatch_id: UUID
    request_id: UUID
    resource_id: UUID
    quantity_dispatched: int
    resource_provider: str
    dispatched_at: datetime
    notes: Optional[str] = None
    message: str


# ===== RESOURCE SCHEMAS =====

class ResourceCreate(BaseModel):
    """Schema for creating a new resource."""
    model_config = ConfigDict(from_attributes=True)
    
    resource_type: ResourceType
    provider_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        examples=["Andheri Fire Brigade", "Red Cross Mumbai"]
    )
    quantity_available: int = Field(
        ...,
        ge=0,
        examples=[10, 50]
    )
    latitude: float = Field(
        ...,
        ge=-90.0,
        le=90.0,
        examples=[19.1197]
    )
    longitude: float = Field(
        ...,
        ge=-180.0,
        le=180.0,
        examples=[72.8464]
    )
    location_name: str = Field(
        ...,
        min_length=1,
        max_length=255,
        examples=["Andheri Fire Station"]
    )


class ResourceUpdate(BaseModel):
    """Schema for updating resource availability."""
    model_config = ConfigDict(from_attributes=True)
    
    quantity_available: Optional[int] = Field(None, ge=0)
    availability_status: Optional[AvailabilityStatus] = None


class ResourceResponse(BaseModel):
    """Schema for resource API response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    resource_type: ResourceType
    provider_name: str
    quantity_available: int
    latitude: float
    longitude: float
    location_name: str
    availability_status: AvailabilityStatus
    created_at: datetime
    last_updated: datetime


# ===== RESOURCE MATCHING SCHEMAS =====

class ResourceMatch(BaseModel):
    """
    Schema for a matched resource with scoring.
    
    Used when displaying potential resource matches for a crisis request.
    """
    model_config = ConfigDict(from_attributes=True)
    
    resource: ResourceResponse
    match_score: float = Field(
        ...,
        ge=0.0,
        le=100.0,
        description="Match quality score (0-100)"
    )
    distance_km: float = Field(
        ...,
        ge=0.0,
        description="Distance from request location in kilometers"
    )
    fulfillment_ratio: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Ratio of request quantity that can be fulfilled (0-1)"
    )
    reasoning: list[str] = Field(
        ...,
        description="Reasoning for match score",
        examples=[
            ["1.8km away (score: 91)", "Can fulfill 100% of request (score: 100)"]
        ]
    )


class ResourceMatchList(BaseModel):
    """Schema for list of resource matches."""
    model_config = ConfigDict(from_attributes=True)
    
    request_id: UUID
    matches: list[ResourceMatch]
    total_matches: int


# ===== DISPATCH LOG SCHEMAS =====

class DispatchLogCreate(BaseModel):
    """Schema for creating a dispatch log."""
    model_config = ConfigDict(from_attributes=True)
    
    request_id: UUID
    resource_id: UUID
    dispatched_quantity: int = Field(..., gt=0)
    notes: Optional[str] = Field(None, max_length=1000)


class DispatchLogResponse(BaseModel):
    """Schema for dispatch log API response."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    request_id: UUID
    resource_id: UUID
    dispatched_quantity: int
    dispatched_at: datetime
    notes: Optional[str] = None


# ===== UTILITY SCHEMAS =====

class HealthCheckResponse(BaseModel):
    """Schema for health check endpoint response."""
    status: str
    database: str


class MessageResponse(BaseModel):
    """Generic message response schema."""
    message: str
