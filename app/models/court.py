import enum
import uuid

from sqlalchemy import Boolean, Column, Enum, Numeric, String
from sqlalchemy.dialects.postgresql import UUID

from app.core.database import Base


class SportType(str, enum.Enum):
    netball = "netball"
    cricket = "cricket"
    tennis = "tennis"
    badminton = "badminton"
    futsal = "futsal"
    other = "other"


class Court(Base):
    __tablename__ = "courts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    sport_type = Column(Enum(SportType), nullable=False)
    rate_per_hour = Column(Numeric(10, 2), nullable=False)
    is_active = Column(Boolean, default=True)