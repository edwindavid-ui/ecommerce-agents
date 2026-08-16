from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field

from app.auth.service import AuthService
from app.schemas.user import UserCreate, UserLogin
from app.auth.deps import get_current_user_id

router = APIRouter(prefix="/auth", tags=["auth"])
service = AuthService()

class ChangePasswordRequest(BaseModel):
    old_password: str = Field(..., min_length=8)
    new_password: str = Field(..., min_length=8)


@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserCreate):
    try:
        result = await service.register_user(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return result


@router.post("/login")
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    OAuth2 compatible token login, get an access token for future requests.
    Note: OAuth2PasswordRequestForm uses 'username' instead of 'email' in the payload.
    """
    try:
        login_payload = UserLogin(email=form_data.username, password=form_data.password)
        result = await service.login_user(login_payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    return result


@router.post("/change-password", status_code=status.HTTP_200_OK)
async def change_password(
    payload: ChangePasswordRequest,
    current_user_id: str = Depends(get_current_user_id)
):
    """
    Allows an authenticated user to securely update their password.
    """
    try:
        await service.change_password(current_user_id, payload.old_password, payload.new_password)
        return {"message": "Password changed successfully"}
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))