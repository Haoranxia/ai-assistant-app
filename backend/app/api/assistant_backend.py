from fastapi import APIRouter, Depends
from app.services import assistant_service
from app.services import session_service

router = APIRouter()

@router.post("/new_chat")
def new_chat(
    user_id: str = Depends(session_service.get_current_user_id)
):
    """ 
    Endpoint for starting a new chat which means we must return a unique session_id
    to identify the chat with
    """
    session_id = assistant_service.create_new_session(user_id)
    return {"session_id": session_id}   # frontend will store this for that session


@router.delete("/close_chat/{session_id}")
def close_chat(
    session_id: str = None,
    user_id: str = Depends(session_service.get_current_user_id),
):
    """ 
    Endpoint for closing some chat corresponding to some session_id
    """
    if session_id is None: 
        return {"status": "error"}
    
    assistant_service.delete_session(user_id, session_id)
    return {"status": "deletion successful"}



@router.post("/chat/{session_id}/message")
def assistant_chat(
    request: assistant_service.AssistantChatRequest,
    session_id: str = None,
    user_id: str = Depends(session_service.get_current_user_id)
):
    """ 
    Endpoint for spinning up an agent to process the prompt.
    User interacts with agent via chat messages through this API endpoint
    """
    prompt = request.prompt
    response = assistant_service.run_calendar_assistant(user_id, session_id, prompt)
    
    return {"response": response}