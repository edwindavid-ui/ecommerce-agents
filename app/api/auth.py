from fastapi import APIRouter, HTTPException, status

from app.auth.service import AuthService
from app.schemas.user import UserCreate, UserLogin

router = APIRouter(prefix="/auth", tags=["auth"])
service = AuthService()


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register_user(payload: UserCreate):
    try:
        result = service.register_user(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
    return result


@router.post("/login")
def login_user(payload: UserLogin):
    try:
        result = service.login_user(payload)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials") from exc
    return result
