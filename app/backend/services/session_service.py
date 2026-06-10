from datetime import datetime, timedelta
from jose import JWTError, jwt
import secrets

# This part implements session management using JWT 

# For development only - use environment variables in production
SECRET_KEY = "your-super-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

def generate_session_token(user_id: str) -> str:
    """ 
    Generate a JWT token based on the users id and temporal information
    """
    payload = {
        "user_id": user_id,
        "exp": datetime.now(datetime.timezone.utc) + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS),
        "iat": datetime.now(datetime.timezone.utc),
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


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
        return None
    

def generate_new_user_id() -> str:
    """ 
    Generate a new unique user ID
    """
    return secrets.token_hex(8)