from fastapi import APIRouter, HTTPException, Request, Depends
from app.services import auth_service, session_service

# TODO: Only enable this for local development. OAuth2 wants to use https but its a hassle :p
import os
os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

router = APIRouter()


@router.get("/google/login")
def google_login():
    """ 
    Starts the authentication process for our api application
    Establish a personalized login transaction with the user with our app
    """
    response = auth_service.get_authorization_url()
    return response


@router.get("/google/callback")
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
    # We return creds but also store it somewhere
    user_id = session_service.generate_new_user_id()
    _ = auth_service.exchange_callback_for_credentails(
        authorization_response=str(request.url),
        state=expected_state,
        code_verifier=request.cookies.get("code_verifier"),
        user_id=user_id
    )

    # Return JWT token to user that they can use to identify themselves with
    jwt_token = session_service.generate_session_token(user_id)
    return {"access_token": jwt_token, "token_type": "bearer"}


@router.get("/google/status")
def google_status():
    """ 
    Check if our backend is up and running
    """
    return {"status": "ok"}


@router.post("/google/logout")
def google_logout(user_id: str = Depends(session_service.get_current_user_id)):
    """ 
    Logs the user out 
    """
    auth_service.forget_credentials(user_id)
    return {"status": "logged out"}


# For testing whether the JWT token stuff works
@router.get("/me")
def auth_me(user_id: str = Depends(session_service.get_current_user_id)):
    """ 
    Get the id associated with the bearer of the token
    """
    return {"user_id": user_id}