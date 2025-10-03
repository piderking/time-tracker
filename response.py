from pydantic import BaseModel
from enum import Enum
from typing import List
from model import Event, Project, HeartBeat


class Response(BaseModel):
    content: str
    message: str | None = None
    error: bool = False


class ListResponse(Response):
    content: List[str]


class IntResponse(Response):
    content: int


class BoolResponse(Response):
    content: bool


class EventResponse(Response):
    content: Event


class EventsResponse(Response):
    content: List[Event]


class ProjectResponse(Response):
    content: Project
    message: str = "Singular Project Resonse"


class ProjectsResponse(Response):
    content: List[Project]


class ErrorResponse(Response):
    pass


class ErrorMessage(Enum):
    validation = "Validation Error"
    query = "Query Error"
    not_found = "Value not found"
    duplicate = "Duplicate Value"
    server_error = "Server Error"


def to_response(error: ErrorMessage, message) -> ErrorResponse:
    return ErrorResponse(content=error, message=message, error=True)
