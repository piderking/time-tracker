from tinydb import TinyDB, Query
from model import Project, Event
from typing import Optional
db = TinyDB("data/db.json")


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
