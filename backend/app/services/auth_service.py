from pathlib import Path

from fastapi.responses import RedirectResponse

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow

# This file contains functionality that the API will make use of
#TODO: Remove hardcoded things
CLIENT_SECRET_FILE = Path("app/creds/credentials.json")
CREDS_DIR = Path("app/database") # Where we store the credentials
SCOPES = ["https://www.googleapis.com/auth/calendar"]
REDIRECT_URI = "http://localhost:8000/auth/google/callback" # Used in auth_backend.py


def get_token_file(user_id: str) -> Path:
    """ 
    Get the token file path associated with this specific user
    """
    # create custom directory for this user
    user_creds_dir = CREDS_DIR / user_id
    user_creds_dir.mkdir(parents=True, exist_ok=True)
    return user_creds_dir / "token.json"


def create_flow(state: str | None = None) -> Flow:
    """ 
    Creates the Flow object that allows us to perform OAuth processes.
    The Flow object stores all the information required to perform an OAuth process
    and contains functionality for performing such a process
    """
    flow = Flow.from_client_secrets_file(
        str(CLIENT_SECRET_FILE),
        scopes=SCOPES,
        state=state,
    )
    flow.redirect_uri = REDIRECT_URI
    return flow


def get_authorization_url() -> RedirectResponse:
    """ 
    Using the created Flow object we return an url through which the
    user must authenticate
    """
    flow = create_flow()
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="consent",
    )
    response = RedirectResponse(url=authorization_url)
    response.set_cookie("google_oauth_state", state, httponly=True, samesite="lax")
    response.set_cookie("code_verifier", flow.code_verifier, httponly=True, samesite="lax")
    return response


def exchange_callback_for_credentails(
        authorization_response: str,
        state: str,
        code_verifier: str,
        user_id: str,
) -> Credentials:
    """ 
    After the user has "logged" in via Google we get an auth. response
    back. We use this response to go about obtaining the token
    """
    flow = create_flow(state=state)
    flow.code_verifier = code_verifier
    flow.fetch_token(authorization_response=authorization_response)
    credentials = flow.credentials
    save_credentials(user_id, credentials)
    return credentials


def save_credentials(user_id: str, credentials: Credentials) -> None:
    """ 
    Store the obtained credentials (access token) that we obtain
    from the user. 
    """
    # For now each user has their own directory and token.json file
    # where their token is stored
    token_file = get_token_file(user_id)
    token_file.write_text(data=credentials.to_json(), encoding='utf-8')


def load_credentails(user_id: str) -> Credentials | None:
    """ 
    Return a credential object based on the users' token
    """
    token_file = get_token_file(user_id)
    if not token_file.exists():
        return None

    return Credentials.from_authorized_user_file(
        str(token_file),
        scopes=SCOPES,
    )


def get_valid_credentials(user_id: str) -> Credentials | None: 
    """ 
    Check if credentials are valid. Whether it exists or is expired
    """
    credentials = load_credentails(user_id)
    
    if credentials is None:
        return None
    
    if credentials.valid:
        return credentials
    
    # Refresh token if it doesnt exist. Assumes the user has already
    # specified a token before and therefore the 'Credentials' object
    # is not None. So we can reuse that object with a refresh(Request())
    if credentials.expired and credentials.refresh_token:
        credentials.refresh(Request())
        save_credentials(user_id=user_id, credentials=credentials)
        return credentials

    return None


def forget_credentials(user_id: str) -> None:
    """ 
    Logs out the user by forgetting the credentials
    """
    token_file = get_token_file(user_id)
    token_file.unlink(missing_ok=True)
