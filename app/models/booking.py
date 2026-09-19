import enum
import uuid

from sqlalchemy import Column, DateTime, Enum, ForeignKey, Numeric
from sqlalchemy.dialects.postgresql import ExcludeConstraint, TSTZRANGE, UUID
from sqlalchemy.sql import func

from app.core.database import Base


class BookingStatus(str, enum.Enum):
    pending = "pending"      
    confirmed = "confirmed"  
    cancelled = "cancelled"  


class Booking(Base):
    __tablename__ = "bookings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    court_id = Column(UUID(as_uuid=True), ForeignKey("courts.id"), nullable=False)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time = Column(DateTime(timezone=True), nullable=False)

    total_amount = Column(Numeric(10, 2), nullable=False)
    status = Column(Enum(BookingStatus), default=BookingStatus.pending, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        
        ExcludeConstraint(
            (court_id, "="),
            (func.tstzrange(start_time, end_time), "&&"),
            using="gist",
            name="no_overlapping_bookings",
            where=(status != BookingStatus.cancelled),
        ),
    )