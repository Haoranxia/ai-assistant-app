from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class CalendarEvent(BaseModel):
    title: str
    start: str 
    end: str
    description: str

@router.get("/check")
def calendar_check():
    return {"status": "ok"}

@router.get("/events")
def calendar_get_events():
    return {"GET_EVENTS"}   # todo: have some DB or API call google calender with events

@router.post("/events")
def calendar_post_event(event: CalenderEvent):
    return {"status": "ok"}