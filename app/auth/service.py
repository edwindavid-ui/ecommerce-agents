import os
import jwt
from datetime import datetime, timedelta, timezone
from app.db.mongodb import user_collection
from passlib.context import CryptContext
from app.schemas.user import UserCreate, UserLogin

# Load JWT configs from .env
SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key_if_env_fails")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60))

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
        now_str = datetime.now(timezone.utc).isoformat()

        user = {
            "first_name": user_data.first_name,
            "last_name": user_data.last_name,
            "email": email,
            "role": user_data.role,
            "password": hashed_password,
            "status": "active",
            "preferences": {
                "currency": "NGN",
                "preferred_categories": [],
                "preferred_brands": [],
                "default_max_budget": None
            },
            "created_at": now_str,
            "updated_at": now_str
        }

        result = await user_collection.insert_one(user)
        user["_id"] = result.inserted_id

        return {
            "message": "User registered successfully",
            "user": {
                "id": str(result.inserted_id),
                "first_name": user["first_name"],
                "last_name": user["last_name"],
                "email": user["email"],
                "role": user["role"],
                "status": user["status"],
                "preferences": user["preferences"],
                "created_at": user["created_at"],
                "updated_at": user["updated_at"]
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
                "first_name": user.get("first_name", ""),
                "last_name": user.get("last_name", ""),
                "email": user["email"],
                "role": user.get("role", "buyer"),
                "status": user.get("status", "active"),
                "preferences": user.get("preferences", {}),
                "created_at": user.get("created_at"),
                "updated_at": user.get("updated_at")
            },
            "access_token": self._create_token(user),
            "token_type": "bearer",
        }

    async def change_password(self, user_id: str, old_password: str, new_password: str) -> bool:
        from bson import ObjectId
        user = await user_collection.find_one({"_id": ObjectId(user_id)})
        if not user or not verify_password(old_password, user["password"]):
            raise ValueError("Incorrect old password")

        hashed_new_password = get_password_hash(new_password)
        now_str = datetime.now(timezone.utc).isoformat()

        result = await user_collection.update_one(
            {"_id": ObjectId(user_id)},
            {"$set": {"password": hashed_new_password, "updated_at": now_str}}
        )
        return result.modified_count > 0

    def _create_token(self, user: dict) -> str:
        # Standard JWT claims: 'sub' (subject/user_id) and 'exp' (expiration)
        user_id = str(user.get("_id") or user.get("id"))
        expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        payload = {
            "sub": user_id,
            "email": user["email"],
            "role": user.get("role", "buyer"),
            "exp": expire
        }
        
        encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt