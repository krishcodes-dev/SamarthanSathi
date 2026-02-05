"""
Database models for SamarthanSathi crisis-response system.
"""
import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    CHAR, TypeDecorator,
    DateTime, String, Integer, Float, Enum, Text,
    ForeignKey, Index, UUID, JSON
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.core.database import Base


# UUID type compatibility for SQLite and PostgreSQL
class GUID(TypeDecorator):
    """Platform-independent GUID type.
    
    Uses PostgreSQL's UUID type, otherwise uses CHAR(36) for SQLite.
    """
    impl = CHAR
    cache_ok = True
    
    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))
    
    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            else:
                return str(value)
    
    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                value = uuid.UUID(value)
            return value


# ===== ENUMS =====

class RequestStatus(str, enum.Enum):
    """Status of a crisis request."""
    NEW = "new"
    IN_PROGRESS = "in_progress"  # Resource dispatched but request not fully resolved
    DISPATCHED = "dispatched"
    RESOLVED = "resolved"
    INVALID = "invalid"


class ResourceType(str, enum.Enum):
    """Type of resource available."""
    MEDICAL = "medical"
    FOOD = "food"
    WATER = "water"
    SHELTER = "shelter"
    RESCUE = "rescue"
    TRANSPORT = "transport"
    BLANKETS = "blankets"
    OTHER = "other"


class AvailabilityStatus(str, enum.Enum):
    """Availability status of a resource."""
    AVAILABLE = "available"
    PARTIALLY_AVAILABLE = "partially_available"
    UNAVAILABLE = "unavailable"
    DISPATCHED = "dispatched"


# ===== MODELS =====

class CrisisRequest(Base):
    """
    Crisis request submitted by affected individuals or observers.
    
    Stores raw text input and AI-generated analysis (extraction + urgency).
    """
    __tablename__ = "crisis_requests"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Raw input
    raw_text: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # AI-generated analysis (stored as JSONB)
    extraction: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Entity extraction output: {need_type, location, quantity, contact, etc.}"
    )
    
    urgency_analysis: Mapped[Optional[dict]] = mapped_column(
        JSON,
        nullable=True,
        comment="Urgency scoring output: {score, level, reasoning, confidence}"
    )
    
    # Status tracking
    status: Mapped[RequestStatus] = mapped_column(
        Enum(RequestStatus, name="request_status_enum"),
        default=RequestStatus.NEW,
        nullable=False,
        index=True  # Index for filtering by status
    )
    
    # Relationships
    dispatch_logs: Mapped[list["DispatchLog"]] = relationship(
        "DispatchLog",
        back_populates="request",
        cascade="all, delete-orphan"
    )
    
    # Indexes for performance
    __table_args__ = (
        # Composite index for urgency-based queries
        Index(
            'ix_crisis_requests_urgency_status',
            'status',
            # urgency_analysis->>'level' would be ideal but we'll query in Python
        ),
        # Index on created_at for time-based queries
        Index('ix_crisis_requests_created_at', 'created_at'),
    )
    
    def __repr__(self) -> str:
        return f"<CrisisRequest(id={self.id}, status={self.status.value})>"


class Resource(Base):
    """
    Available resource that can be dispatched to crisis locations.
    
    Represents physical resources (ambulances, food supplies, etc.) with
    quantity tracking and geolocation.
    """
    __tablename__ = "resources"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Resource metadata
    resource_type: Mapped[ResourceType] = mapped_column(
        Enum(ResourceType, name="resource_type_enum"),
        nullable=False,
        index=True  # Index for filtering by type
    )
    
    provider_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Organization or individual providing the resource"
    )
    
    # Quantity tracking
    quantity_available: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        comment="Current available quantity"
    )
    
    # Geolocation
    latitude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="GPS latitude coordinate"
    )
    
    longitude: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        comment="GPS longitude coordinate"
    )
    
    location_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        comment="Human-readable location (e.g., 'Andheri Fire Station')"
    )
    
    # Status
    availability_status: Mapped[AvailabilityStatus] = mapped_column(
        Enum(AvailabilityStatus, name="availability_status_enum"),
        default=AvailabilityStatus.AVAILABLE,
        nullable=False,
        index=True  # Index for filtering by availability
    )
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    last_updated: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )
    
    # Relationships
    dispatch_logs: Mapped[list["DispatchLog"]] = relationship(
        "DispatchLog",
        back_populates="resource",
        cascade="all, delete-orphan"
    )
    
    # Indexes for geospatial and type-based queries
    __table_args__ = (
        # Composite index for resource matching queries
        Index(
            'ix_resources_type_availability',
            'resource_type',
            'availability_status'
        ),
        # Index for geospatial bounding box queries
        Index('ix_resources_location', 'latitude', 'longitude'),
    )
    
    def __repr__(self) -> str:
        return f"<Resource(id={self.id}, type={self.resource_type.value}, qty={self.quantity_available})>"


class DispatchLog(Base):
    """
    Log of resource dispatches to crisis requests.
    
    Tracks which resources were dispatched to which requests, including
    quantity and timestamp for audit trail.
    """
    __tablename__ = "dispatch_logs"
    
    # Primary key
    id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Foreign keys
    request_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("crisis_requests.id", ondelete="CASCADE"),
        nullable=False,
        index=True  # Index for request-based queries
    )
    
    resource_id: Mapped[uuid.UUID] = mapped_column(
        GUID,
        ForeignKey("resources.id", ondelete="CASCADE"),
        nullable=False,
        index=True  # Index for resource-based queries
    )
    
    # Dispatch details
    dispatched_quantity: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Quantity of resource dispatched"
    )
    
    dispatched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    # Optional notes
    notes: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Additional dispatch notes or instructions"
    )
    
    # Relationships
    request: Mapped["CrisisRequest"] = relationship(
        "CrisisRequest",
        back_populates="dispatch_logs"
    )
    
    resource: Mapped["Resource"] = relationship(
        "Resource",
        back_populates="dispatch_logs"
    )
    
    # Index for time-based audit queries
    __table_args__ = (
        Index('ix_dispatch_logs_dispatched_at', 'dispatched_at'),
    )
    
    def __repr__(self) -> str:
        return f"<DispatchLog(id={self.id}, qty={self.dispatched_quantity})>"
