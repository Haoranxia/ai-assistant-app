from fastapi import APIRouter, Depends
from app.services import calendar_service
from app.services import session_service

router = APIRouter()


@router.get("/check")
def calendar_check():
    """ 
    Check status of calendar backend
    """
    return {"status": "ok"}


@router.get("/events")
def calendar_get_events(user_id: str = Depends(session_service.get_current_user_id)):
    """ 
    Get the events and return them
    """
    # We can interact with the Google calendar through this "service" object
    service = calendar_service.get_calendar_service_for_user(user_id)
    events = calendar_service.get_events(service)
    return {"events": events}


@router.post("/events/delete")
def calendar_delete_event(
    event_id: str, 
    user_id: str = Depends(session_service.get_current_user_id)
):
    """ 
    Delete an event
    """
    service = calendar_service.get_calendar_service_for_user(user_id)
    calendar_service.delete_event(service, event_id)
    return {"status": "ok"}



@router.post("/events")
def calendar_post_event(
    event: calendar_service.CalendarEvent,
    user_id: str = Depends(session_service.get_current_user_id)
):
    """ 
    TODO
    """
    service = calendar_service.get_calendar_service_for_user(user_id)
    calendar_event = calendar_service.create_event(service, event)

    return calendar_event