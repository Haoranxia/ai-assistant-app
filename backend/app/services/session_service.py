import secrets

from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer

# This part implements session management using JWT 

# For development only - use environment variables in production
SECRET_KEY = "your-super-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

# Create a dependency object that knows how to extract a Bearer token from an incoming HTTP request
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def generate_session_token(user_id: str) -> str:
    """ 
    Generate a JWT token based on the users id and temporal information
    """
    payload = {
        "user_id": user_id,
        "exp": datetime.now(timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS),
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


def get_current_user_id(token: str = Depends(oauth2_scheme)) -> str:
    """ 
    When this is called, it must execute the dependency captured by "Depends(oauth2_scheme)" first
    This then extracts the token from our HTTP request and passes it to our function arg
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return user_id
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    

def verify_session_token(token: str) -> str | None:
    """ 
    Verify the token and return user_id if valid.
    Else we return None
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=ALGORITHM)
        user_id = payload.get("user_id")
        return user_id
    
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    

def generate_new_user_id() -> str:
    """ 
    Generate a new unique user ID
    """
    return secrets.token_hex(8)