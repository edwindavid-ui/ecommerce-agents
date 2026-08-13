from datetime import datetime, timedelta, timezone

from app.schemas.user import UserCreate, UserLogin


class AuthService:
    def __init__(self):
        self._users: dict[str, dict] = {}

    def register_user(self, user_data: UserCreate) -> dict:
        email = str(user_data.email)
        if email in self._users:
            raise ValueError("User already exists")

        user = {
            "id": f"user_{len(self._users) + 1}",
            "name": user_data.name,
            "email": email,
            "role": user_data.role,
            "password": user_data.password,
        }
        self._users[email] = user

        return {
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"],
            },
            "access_token": self._create_token(user),
            "token_type": "bearer",
        }

    def login_user(self, login_data: UserLogin) -> dict:
        email = str(login_data.email)
        user = self._users.get(email)
        if user is None or user["password"] != login_data.password:
            raise ValueError("Invalid credentials")

        return {
            "user": {
                "id": user["id"],
                "name": user["name"],
                "email": user["email"],
                "role": user["role"],
            },
            "access_token": self._create_token(user),
            "token_type": "bearer",
        }

    def _create_token(self, user: dict) -> str:
        expiry = datetime.now(timezone.utc) + timedelta(hours=1)
        return f"token_{user['id']}_{expiry.strftime('%Y%m%d%H%M%S')}" 
