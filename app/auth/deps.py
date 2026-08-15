from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timezone

bearer_scheme = HTTPBearer()

# 2. Define the Dependency
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> str:
    """
    Parses the custom token, checks the expiration date, and returns the user_id.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        # HTTPBearer automatically strips the "Bearer " prefix and extracts just the token string
        token = credentials.credentials
        
        # Your token format looks like: token_64df..._20260815123000
        parts = token.split("_")
        
        if len(parts) != 3 or parts[0] != "token":
            raise credentials_exception
            
        user_id = parts[1]
        expiry_str = parts[2]
        
        expiry_date = datetime.strptime(expiry_str, "%Y%m%d%H%M%S").replace(tzinfo=timezone.utc)
        
        if datetime.now(timezone.utc) > expiry_date:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Token has expired"
            )
            
        return user_id
        
    except (ValueError, IndexError):
        raise credentials_exception
    except Exception:
        raise credentials_exception
 