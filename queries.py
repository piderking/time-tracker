from tinydb import Query
from typing import List
from datetime import timedelta, datetime, timezone
from model import Event
from db import db
from config import logger
Project = Query()

# Opperations


def set_event_ongoing_status(uuids: List[str], status: bool):
    """
    Returns a function suitable for db.update() that modifies the 'ongoing'
    status of a specific event identified by its UUID.
    """
    def modifier(doc):
        # 1. Get the events dictionary
        target_uuids = uuids
        events = doc.get('events')

        for evt in events:
            if len(target_uuids) <= 0:
                break  # escape the loop early

            for idx, uuid in enumerate(target_uuids):
                if events.get(uuid):
                    doc["events"][uuid]["ongoing"] = status
                    target_uuids.pop(idx)
                    logger.debug(f"Found {uuid} and updated it")
                    break

        # 2. Check if the target UUID exists and modify the nested field in-place
    return modifier

# Queries


def get_expired_events(duration: timedelta) -> List[str]:  # uuids
    qr = db.all()

    output = []

    for project in qr:
        ct = datetime.now(timezone.utc).replace(tzinfo=None)
        for t in project["events"].values():
            event = Event(**t)
            if not event.ongoing:
                logger.debug(f"Event: {event.title} is not ongoing")
                continue
            if ct - event.segements[-1].time >= duration:
                logger.debug(f"Event: {event.title} has expired.")
                output.append(event.uuid)

            else:
                dr = str(ct - event.segements[-1].time)
                logger.debug(
                    f"Event: {event.title} hasn't expired yet. Duration is  {dr}")
    return output
