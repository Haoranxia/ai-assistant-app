from typing import Any, List

from smolagents import tool
import app.services.calendar_service as cs


class CalendarTools:
    """ 
    Class encapsulating calendar tools so the user_id is always known when calling tools
    and the agent/LLM itself does not have access user_id
    """
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.service = cs.get_calendar_service_for_user(self.user_id)

    @tool
    def get_event_tool(self, max_results=10) -> List:
        """ 
        A tool that gets a list of calendar events via our API backend which connects to 
        the user's google calendar.
        Args:
            max_results: the number of results (calendar events) to return 
        """
        return cs.get_events(self.service, max_results)
    

    @tool
    def create_event_tool(self, event: cs.CalendarEvent) -> Any:
        """ 
        A tool that creates a calendar event via our API backend which connects to 
        the user's google calendar.
        Args:
            event: the event we want to create which follows the CalendarEvent format defined as follows:     
                    title: str
                    start: str 
                    end: str
                    description: str
        """
        # Validate input
        return cs.create_event(self.service, event)
    
    @tool
    def delete_event_tool(self, event_description: str) -> Any:
        """ 
        A tool that deletes a calendar event via our API backend.
        Args:
            event_description:  description of the event we wish to delete
        """
        # TODO: Parse the event description into something fairly concrete (schema-wise)
        # Check if we can delete it directly if information is sufficiently clear
        # If not, scan through our list of events and delete the on matching it
        # If event does not exist, return that we did not find the event to delete
        return {"status": "event deleted"}
