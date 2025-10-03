from tinydb import TinyDB, Query
from model import Project, Event, HeartBeat
from typing import Optional
db = TinyDB("data/db.json")


def add_project(project: Project) -> bool:
    pass


def add_event(project_uuid: str, event: Event) -> bool:
    pass


def add_heart_beat(uuid: str, heart: HeartBeat) -> int:

    db.update(lambda p: p["events"][uuid].update(
        {"ongoing": True}), Query().events[uuid].exists())

    items = db.update(lambda p: p["events"][uuid]["segements"].append(
        heart.model_dump(mode="json")), Query().events[uuid].exists())

    return len(items)


def get_event_by_id(id: str) -> Optional[Event]:
    res = db.search(Query().events[id].exists())

    if len(res) > 0:
        return Event(**res[0]["events"][id])

    return None


def get_project_by_id(id: str) -> Optional[Project]:
    res = db.search(Query().uuid == id)

    print(res)
    try:
        return Project(**res[0])
    except Exception as e:
        return None
