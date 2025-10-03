from pydantic import BaseModel, AnyHttpUrl, Field, field_validator
from uuid import uuid4
from typing import Optional, List, Dict
from datetime import datetime, timedelta, timezone
from enum import Enum

from pydantic import field_serializer


class HeartBeatLocation(BaseModel):
    file: Optional[str] = None
    url: Optional[str] = None
    coordinates: Optional[dict[str, float]] = None


class HeartBeat(BaseModel):
    # Different Things Happen in Event
    category: str
    location: str
    content: dict[str, Optional[str]]

    time: datetime = Field(default_factory=datetime.utcnow)


class NewHeartBeat(HeartBeat):
    time: None

    def into(self) -> HeartBeat:
        return HeartBeat(**dict(self.model_dump() | {"time": datetime.now(timezone.utc).replace(tzinfo=None)}))


class Event(BaseModel):
    uuid: Optional[str] = None

    title: Optional[str] = None
    icon: Optional[str] = None
    content: Optional[str] = None
    # ALWAYS HAS AT LEAST ONCE
    segements: List[HeartBeat] = Field(..., min_length=1)
    ongoing: bool = False

    async def duration(self) -> timedelta:
        self.start_time() - self.end_time()

    async def start_time(self) -> datetime:
        return self.segements[0]

    async def end_time(self) -> datetime:
        if self.ongoing:
            return datetime.now(timezone.utc)

        return self.segements[-1]


# Example: Job
class Project(BaseModel):
    uuid: Optional[str] = None

    title: str
    icon: Optional[str] = None
    # Markdown -- Rendered on Server
    content: Optional[str] = None

    # uuid of events...
    events: Dict[str, Event] = Field(default={})
