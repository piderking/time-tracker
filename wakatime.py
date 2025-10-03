import os
import requests
import json
from fastapi_utilities import repeat_every
from dotenv import load_dotenv
from datetime import datetime, timedelta
from pydantic import BaseModel
from model import HeartBeat
from typing import List
from db import db, get_project_by_id
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
    branch: str
    category: str  # category
    project: str
    language: str
    entity: str
    time: float

    def into(self) -> HeartBeat:
        pass


def dt_sort(dates: List[str, datetime]) -> List[datetime]:
    # event uuid: last one
    return []


@repeat_every(seconds=90)  # every 90 secondsds
async def fetch_wakatime():

    # Event: (project) + (branch)

    url = f"{base_url}/users/current/heartbeats?date={datetime.strftime('%Y-%m-%d')}"

    try:

        response = requests.get(url, headers=headers)

        response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx)
        data = response.json()["data"]  # list of raw WakatimeHeartBeat

        wakatime_project = get_project_by_id("wakatime")

        if wakatime_project is None:
            # TODO create wakatime project here
            pass

        lasts = {v.uuid: v.end_time()
                 for v in wakatime_project.events.values()}

        for raw in data:
            hbt = WakatimeHeartBeat(raw)
            tm = datetime.fromtimestamp(hbt)

    except requests.exceptions.RequestException as e:
        print(f"Error fetching data: {e}")
