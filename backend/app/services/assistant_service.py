import json
import os
import uuid
from pathlib import Path
from typing import Literal

from smolagents import ToolCallingAgent, LiteLLMModel
from pydantic import BaseModel, ValidationError

from app.services.assistant_tools import CalendarTools

# Static variables
SYS_PROMPT_PATH = "database/system_prompt.md" #TODO: Move this to a config file
MAX_RETRIES = 2

model = LiteLLMModel(
    model_id="ollama_chat/qwen2.5:3b-instruct",
    api_base="http://localhost:11434",
    num_ctx=8192,
    temperature=0.2
)


### SCHEMAS
class AgentResponse(BaseModel):
    """ 
    Schema defining the structure of the response our Agent must eventually generate
    """
    status: Literal[
        "done",
        "need_clarification",
        "awaiting_confirmation",
        "failed",
    ]
    message: str
    pending_action: dict | None = None
    missing_fields: list[str] = []


### MISC FUNCTIONS
def create_new_session(user_id: str) -> str:
    """ 
    Create a new context file for the user identified by 'user_id'.
    This session is identified by an unique 'session_id'
    Args:
        user_id: id of the user
    """
    # Generate a new session_id
    session_id = str(uuid.uuid4())
    # Create a new context file using this session_id
    with open(f"database/{user_id}/{session_id}_context.json", 'w', encoding='UTF-8') as _:
        pass

    return session_id

def delete_session(user_id: str, session_id: str):
    """ 
    Deletes the session associated with the parameters
    Args:
        user_id:    id of the user
        session_id: id of the session to be deleted
    """
    file_path = Path(f"database/{user_id}/{session_id}_context.json")
    if os.path.exists(file_path):
        os.remove(file_path)


### CONTEXT (AGENT HISTORY) MANAGEMENT FUNCTIONS
def load_context(context_path: Path) -> str:
    """ 
    Load the system prompt and user specific context into one piece of context
    to be used by the LLM as it's instructions prompt
    """
    with open(SYS_PROMPT_PATH, 'r', encoding='UTF-8') as file:
        system_prompt = file.read()

    # Load context based on user_id
    with open(context_path, 'r', encoding='UTF-8') as json_file:
        state_block = json.load(json_file)

    return f"""
    {system_prompt}

    Current session state:
    ```json
    {state_block}
    ```
    """

def reset_context(context_path: Path):
    """ 
    Reset the context history for the user identified by 'user_id'
    """
    with open(context_path, 'r', encoding='UTF-8') as jf:
        session = json.load(jf)

    session["history"] = []

    with open("context.json", 'w', encoding='UTF-8') as jf:
        json.dump(session, jf, indent=4)

def update_context_file(state: dict, context_path: Path):
    """ 
    Update the context history with the response we got from the agent.
    We first parse response into the proper structure (or validate it)
    Note that the LLM returns JSON? 
    """
    # Load the JSON file
    with open(context_path, "r", encoding="UTF-8") as f:
        session = json.load(f)

    session["history"].append(state)    # Append the new entry

    with open(context_path, "w", encoding="UTF-8") as f:
        json.dump(session, f, indent=4)


### AGENT FUNCTIONS
def build_agent(user_id: str, context: str) -> ToolCallingAgent:
    """ 
    Constructs an agent using relevant information for the specific user
    as specified by user_id
    """
    # Construct agent
    calendar_tools = CalendarTools(user_id=user_id)
    tools_list = [calendar_tools.get_event_tool]
    return ToolCallingAgent(
            model=model,
            tools=tools_list,
            max_steps=3,
            verbosity=1,
            grammar=None,
            description=None,
            instructions=context
    )

def run_calendar_assistant(user_id: str, session_id: str, prompt: str) -> str:
    """ 
    Run the agent with to solve calendar related tasks as specified by the prompt. 
    Args:
        user_id:    unique id of this user used to identify who it is.
        session_id: unique id corresponding to a specific chat session.
        prompt:     a string containing the literal prompt that the user typed to sent to the agent.
    """
    context_path = Path(f"database/{user_id}/{session_id}_context.json")
    context = load_context(context_path)    # Load agent state based on user_id

    for _ in range(MAX_RETRIES):
        agent = build_agent(user_id, context)   # Construct the agent for this user

        # Run agent
        # Note that agent.run() implements a lot of the heavy lifting for us
        # 1. thought-action-observation loop is implemented here and stepped through step-wise
        # 2. automatically handling of context window (logging history) is also handled
        #    as we step through the loop, the history/context/logs grow. This is automatically managed
        # 3. generation of the tool call JSON file and execution of the tool is handled
        response = agent.run(prompt)

        try:
            validated_response: AgentResponse = AgentResponse.model_validate(response)

            if validated_response.status == "need_clarification":
                # Update the context history with info of the last thought-action-observation context
                # Ask user for clarification
                update_context_file(validated_response, context_path)
        
            elif validated_response.status == "awaiting_confirmation":
                update_context_file(validated_response, context_path)
            
            elif validated_response.status == "failed":
                reset_context(context_path)

            elif validated_response.status == "done":
                reset_context(context_path)

            # The message contains the response of the LLM to the prompt
            return validated_response.message

        except ValidationError as e:
            # Ask LLM to fix the output
            # TODO: Can probably make this code prettier
            print("Validation Failed")
            print(e)
            prompt += f"""
                    The previous response was invalid.
                    Validation error:
                    {e}
                    Please return ONLY valid output conforming to the schema below and wrapped in the 'final_answer' function call:
                    final_answer({{
                    "status": "done | need_clarification | awaiting_confirmation | failed",
                    "message": "...",
                    "pending_action": None or {...},
                    "missing_fields": [...]
                    }})
                    """