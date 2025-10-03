from fastapi_utilities import repeat_every, repeat_at
from fastapi import FastAPI, Query as FQuery
from model import Project, Event, HeartBeat, NewHeartBeat
from db import db, get_event_by_id, get_project_by_id, add_heart_beat
from tinydb import Query
from response import BoolResponse, EventResponse, EventsResponse, ProjectsResponse, ProjectResponse, IntResponse, Response,  ErrorMessage, to_response, ErrorResponse, ListResponse
from uuid import uuid4
from typing import Optional, Any, List, Dict
from json import loads
from datetime import timedelta
from queries import set_event_ongoing_status, get_expired_events
from contextlib import asynccontextmanager

from config import logger, iteration
from wakatime import fetch_wakatime
# --- Start Up Code --


# @app.on_event("startup")

# cron_iter = 0
# Define an asynchronous context manager for the application's lifespan


@repeat_every(seconds=5)
async def minute_loop():
    # cron_iter += 1  # noqa
    logger.info(f"[MINUTE_LOOP]: Itteration")
    expired = get_expired_events(timedelta(seconds=2))
    status = db.update(set_event_ongoing_status(
        expired, False), Query().events.any(expired))
    logger.info(
        f"[MINUTE_LOOP]: Expired the following amount: {len(status)}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Perform startup tasks here
    logger.info("Starting...")

    # Fetch Custom Histories
    # await fetch_wakatime_history()

    await minute_loop()
    yield
    # Shutdown event
    logger.info("Application shutdown initiated.")
    # Perform shutdown tasks here
    logger.info("Resources released.")


app = FastAPI(lifespan=lifespan)


@ app.get("/projects")
async def get_projects(id: Optional[str] = None) -> ProjectResponse | ProjectsResponse | ErrorResponse:

    if id:
        res = get_project_by_id(id)
        if res:
            return ProjectResponse(content=res)
        else:
            return to_response(ErrorMessage.not_found, f"Project: {id} not found!")
    else:
        return ProjectsResponse(content=[Project(**item) for item in db.all()])


@ app.post('/projects/config')
async def config_project(id: str, config: dict[str, Any]) -> IntResponse:
    try:
        if config.get("uuid"):
            config.pop("uuid")
        updated = db.update(config, Query().uuid == id)
        if len(updated) > 0:
            print("Project Config Manually Editted...")
            return IntResponse(content=len(updated), message=f"manually changed the config of {len(updated)} projects")
    except Exception as e:
        raise e
        return to_response(ErrorMessage.server_error, str(e))


@ app.post("/projects/new")
async def new_project(project: Project) -> ProjectResponse | ErrorResponse:
    if db.contains(Query().title == project.title):

        return to_response(ErrorMessage.duplicate, "Item with this title already exsists. Try again with a different title.")
    if not project.uuid or (project.uuid and db.contains(Query().uuid == project.uuid)):
        project.uuid = str(uuid4())
    try:
        db.insert(project.model_dump())
        return ProjectResponse(content=project)
    except Exception as e:
        return to_response(ErrorMessage.server_error, str(e))

# Events


@ app.get("/projects/{uuid}/events")
def all_events(uuid: str) -> EventsResponse:
    proj = get_project_by_id(uuid)

    if proj:
        return EventsResponse(content=proj.events.values())

    return to_response(ErrorMessage.not_found, f"Project ID: {uuid} not found")


@ app.post("/project/{uuid}/events/new")
async def new_event(uuid: str, events: List[Event]) -> ListResponse:
    output = []
    count = 0
    for e in events:
        # Create a uuid for every event
        e.uuid = str(uuid4())
        output.append(e.uuid)
        e.ongoing = True
        items = db.update(lambda p: p["events"].update(
            {e.uuid: e.model_dump(mode="json")}), Query().uuid == uuid)
        count += len(items)

    return ListResponse(
        content=output,
        message=f"Added {count} events to project's ({uuid}) events"
    )


@ app.get("/events/{uuid}")
async def get_event(uuid: str) -> EventResponse | ErrorResponse:
    event = get_event_by_id(uuid)

    if event:
        return EventResponse(content=event, message=f"Event: {uuid}")


@ app.post("/events/{uuid}/start")
async def start_event(uuid: str) -> BoolResponse:
    status = db.update(lambda p: p["events"][uuid].update(
        {"ongoing": True}), Query().events[uuid].exists())
    return BoolResponse(content=len(status) > 0, message="whether started event")


@ app.post("/events/{uuid}/stop")
async def stop_event(uuid: str) -> BoolResponse:
    status = db.update(lambda p: p["events"][uuid].update(
        {"ongoing": False}), Query().events[uuid].exists())
    return BoolResponse(content=len(status) > 0, message="whether stopped event")


@ app.post("/events/{uuid}/hbt")
async def heart_beat(uuid: str, heart: NewHeartBeat) -> int:
    return add_heart_beat(uuid, heart.into())


@ app.get("/")
async def root():
    return "ROOT"
