from typing import Any, List
import datetime

from pydantic import BaseModel
from googleapiclient.discovery import build
from app.services.auth_service import get_valid_credentials


class CalendarEvent(BaseModel):
    """ 
    Simple model for calendar events
    """
    title: str
    start: str
    end: str
    description: str


def get_calendar_service_for_user(user_id: str) -> Any:
    """ 
    Return a "googleapiclient.discovery.Resource" configured to be a calendar
    which we can use to access calendar functionality from
    """
    creds = get_valid_credentials(user_id)
    if creds is None:
        raise RuntimeError(
            f"No Google OAuth credentials stored for user {user_id}"
        )
    
    return build(serviceName="calendar", version="v3", credentials=creds)


def get_events(service: Any, max_results=10) -> List: 
    """ 
    Obtain calendar events 
    """
    now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    return events_result.get("items", [])


def create_event(service: Any, calendar_event: CalendarEvent) -> Any:
    """ 
    Create an event
    """
    event_body = {
        "summary": calendar_event.title,
        "description": calendar_event.description,
        "start": {
            "dateTime": calendar_event.start,
            "timeZone": "UTC",
        },
        "end": {
            "dateTime": calendar_event.end,
            "timeZone": "UTC",
        }
    }
    created_event = (
        service.events().insert(
                calendarId="primary", body=event_body
            ).execute()
        )
    
    return created_event


def delete_event(service: Any, event_id: str):
    """ 
    Delete an event
    """
    service.events().delete(
        calendarId="primary", eventId=event_id
    ).execute()


def patch_event(
        service: Any,
        event_id: str,
        updated_event: CalendarEvent
):
    # TODO: implement patch_event
    pass 


def list_events(
    service: Any,
    time_min: str,
    time_max: str,
    max_results: int=10
):
    """
    Lists max_results events between time_min and time_max
    """
    events_result = (
        service.events()
        .list(
            calendarId="primary",
            timeMin=time_min,
            timeMax=time_max,
            maxResults=max_results,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )
    return events_result.get("items", [])


def search_events(
  service: Any,
  query: str,
  time_min=None,
  time_max=None    
):
    # TODO: Implement search events
    pass