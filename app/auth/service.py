from datetime import datetime, timedelta, timezone
from app.db.mongodb import user_collection
from passlib.context import CryptContext
from app.schemas.user import UserCreate, UserLogin

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

class AuthService:
    async def register_user(self, user_data: UserCreate) -> dict:
        email = str(user_data.email)

        existing_user = await user_collection.find_one({"email": email})
        if existing_user:
            raise ValueError("User already exists")

        hashed_password = get_password_hash(user_data.password)

        user = {
            "name": user_data.name,
            "email": email,
            "role": user_data.role,
            "password": hashed_password,
        }

        result = await user_collection.insert_one(user)

        return {
            "message": "User registered successfully",
            "user": {
                "id": str(result.inserted_id),
                "name": user["name"],
                "email": user["email"],
                "role": user["role"],
            },
            "access_token": self._create_token(user),
            "token_type": "bearer",
        }

    async def login_user(self, login_data: UserLogin) -> dict:
        email = str(login_data.email)
        user = await user_collection.find_one({"email": email})
        if user is None or not verify_password(login_data.password, user["password"]):
            raise ValueError("Invalid credentials")

        return {
            "user": {
                "id": str(user["_id"]),
                "name": user["name"],
                "email": user["email"],
                "role": user["role"],
            },
            "access_token": self._create_token(user),
            "token_type": "bearer",
        }

    def _create_token(self, user: dict) -> str:
        expiry = datetime.now(timezone.utc) + timedelta(hours=1)
        user_id = str(user["_id"])
        return f"token_for_{user_id}_expires_at_{expiry.isoformat()}"
