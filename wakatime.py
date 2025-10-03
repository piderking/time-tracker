import os
import requests
import json
from fastapi_utilities import repeat_every
from dotenv import load_dotenv
from datetime import datetime, timedelta, timezone
from pydantic import BaseModel
from model import HeartBeat, HeartBeatLocation, Project, Event
from config import logger
from typing import List, Optional
from db import db, get_project_by_id, get_event_by_title
from tinydb import Query
load_dotenv(".env")


# Replace with your actual API key
api_key = os.getenv("WAKATIME_API_KEY")
base_url = os.getenv("WAKATIME_API_URL") or "https://wakatime.com/api/v1"
headers = {
    # WakaTime uses Basic Auth with API Key as username and empty password
    "Authorization": f"Basic {api_key}"
}


class WakatimeHeartBeat(BaseModel):
    branch: Optional[str] = None  #
    category: str  # category
    project: str  # event
    language: Optional[str] = None
    entity: str
    time: float

    def event_title(self) -> str:
        output = self.project

        if self.branch:
            output += f"-{self.branch}"

        return output

    def into(self) -> HeartBeat:
        return HeartBeat(
            category=self.category,
            location=HeartBeatLocation(),
            time=datetime.fromtimestamp(self.time, timezone.utc),
            content={
                "project": self.project,
                "branch": self.branch,
                "entity": self.entity,
                "language": self.language
            }



        )


async def fetch_wakatime():
    logger.info("[WAKATIME] Refreshing after 90 seconds")
    # Event: (project) + (branch)

    url = f"{base_url}/users/current/heartbeats?date={datetime.strftime('%Y-%m-%d')}"

    try:

        response = requests.get(url, headers=headers)

        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()["data"]  # list of raw WakatimeHeartBeat

        wakatime_project = get_project_by_id("wakatime")

        if wakatime_project is None:
            # TODO create wakatime project here
            db.insert(Project(
                uuid="wakatime",
                title="Wakatime",
                icon="https://wakatime.com/favicon.ico",
                content="Wakatime Dashboard"
            ).model_dump(mode="json"))

        lasts = {v.title: v.end_time()
                 for v in wakatime_project.events.values()}

        now = datetime.utcnow().replace(tzinfo=None)
        for raw in data:

            # check for all the keys
            hbt = WakatimeHeartBeat(raw)
            tm = datetime.fromtimestamp(hbt)
            hbt_title = hbt.event_title()

            if lasts.get(hbt_title) is None or tm > lasts[hbt_title]:
                # set the latest to the current time
                lasts[hbt_title] = tm
                # add event

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
