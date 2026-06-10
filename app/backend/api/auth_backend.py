from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import RedirectResponse

from services import auth_service

"""
Purpely handles the routing and possible returning of information.
All the functional implementation details are in services
"""


router = APIRouter()

@router.get("/auth/google/login")
def google_login():
    """ 
    Starts the authentication process for our api application
    Establish a personalized login transaction with the user with our app
    """
    authorization_url, state = auth_service.get_authorization_url()
    response = RedirectResponse(authorization_url)
    # Store state in a cookie so we can verify whether its the correct user
    # making the request in the callback
    response.set_cookie(
        key="google_oauth_state",
        value=state,
        httponly=True,
        samesite="lax"
    )
    # Return a "RedirectResponse" so the browser at the users' end
    # knows what to do. User goes to that url, does some stuff there,
    # and then redirects to the /callback below
    return response

@router.get("/auth/google/callback")
def google_callback(request: Request):
    """ 
    After "google_login" the RedirectReponse tells the browser to
    go to the callback endpoint of the api (defined in auth_service.py)

    So here we handle the callback 
    """
    expected_state = request.cookies.get("google_oauth_state")
    received_state = request.query_params.get("state")
    
    if not expected_state:
        raise HTTPException(status_code=400, detail="Missing OAuth state cookie")
    
    if expected_state != received_state:
        raise HTTPException(status_code=400, detail="Invalid OAuth state")
    
    # Do the actual authenticating here and obtain the token/credentials
    # We return creds but also store it somewhere. TODO: Change this
    creds = auth_service.exchange_callback_for_credentails(
        authorization_response=str(request.url),
        state=expected_state
    )

    response = RedirectResponse(url="/auth/google/status")
    response.delete_cookie("google_oauth_state")

    return response

@router.get("/auth/google/status")
def google_status():
    return {"status": "ok"}

@router.post("/auth/google/logout")
def google_logout():
    auth_service.forget_credentials()
    return {"status": "logged out"} # TODO make proper response