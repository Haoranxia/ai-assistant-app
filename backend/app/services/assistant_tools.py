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

    def get_event_tool(self, max_results: int = 10) -> List:
        """ 
        A tool that gets a list of calendar events via our API backend which connects to 
        the user's google calendar.
        Args:
            self: The CalendarTools class instance itself
            max_results: the number of results (calendar events) to return 
        """
        return cs.get_events(self.service, max_results)
    

    def create_event_tool(self, event: cs.CalendarEvent) -> Any:
        """ 
        A tool that creates a calendar event via our API backend which connects to 
        the user's google calendar.
        Args:
            self: The CalendarTools class instance itself
            event: the event we want to create which follows the CalendarEvent format defined as follows:     
                    title: str
                    start: str 
                    end: str
                    description: str
        """
        # Validate input
        return cs.create_event(self.service, event)
    
    def delete_event_tool(self, event_description: str) -> Any:
        """ 
        A tool that deletes a calendar event via our API backend.
        Args:
            self: The CalendarTools class instance itself
            event_description:  description of the event we wish to delete
        """
        # TODO: Parse the event description into something fairly concrete (schema-wise)
        # Check if we can delete it directly if information is sufficiently clear
        # If not, scan through our list of events and delete the on matching it
        # If event does not exist, return that we did not find the event to delete
        return {"status": "event deleted"}



def make_calendar_tools(user_id: str) -> List:
    """ 
    Wrapper function for handling tools that require state. Currently using a simple solution
    but in the future (TODO) use a ContextObject and pass that around the tools.
    """
    tools = CalendarTools(user_id)

    @tool 
    def get_events(max_results: int = 10) -> Any:
        """ 
        A tool that gets a list of calendar events via our API backend which connects to 
        the user's google calendar.
        Args:
            self: The CalendarTools class instance itself
            max_results: the number of results (calendar events) to return 
        """
        return tools.get_event_tool(max_results)
    
    @tool
    def create_event(event: cs.CalendarEvent) -> Any:
        """ 
        A tool that creates a calendar event via our API backend which connects to 
        the user's google calendar.
        Args:
            self: The CalendarTools class instance itself
            event: the event we want to create which follows the CalendarEvent format defined as follows:     
                    title: str
                    start: str 
                    end: str
                    description: str
        """
        return tools.create_event_tool(event)   

    @tool 
    def delete_event(event_description: str) -> Any:
        """ 
        A tool that deletes a calendar event via our API backend.
        Args:
            event_description:  description of the event we wish to delete
        """
        return tools.delete_event_tool(event_description)
    
    return [get_events, create_event, delete_event]


