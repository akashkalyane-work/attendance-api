from datetime import datetime, timedelta, timezone
import jwt
from jwt.exceptions import InvalidTokenError

from fastapi import HTTPException, status


class TokenManager:
    def __init__(
        self,
        secret_key: str,
        access_minutes: int,
        refresh_minutes: int,
        algorithm: str,
    ):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.access_minutes = access_minutes
        self.refresh_minutes = refresh_minutes

    def _access_payload(self, sub: int, role: str, expires: timedelta):
        now = datetime.now(timezone.utc)
        return {
            "sub": str(sub),
            "role": role,
            "iat": now,
            "exp": now + expires,
            "token_type": "access",
        }

    def _refresh_payload(self, sub: int, expires: timedelta):
        now = datetime.now(timezone.utc)
        return {
            "sub": str(sub),
            "iat": now,
            "exp": now + expires,
            "token_type": "refresh",
        }

    def create_access_token(self, user_id: int, role: str) -> str:
        return jwt.encode(
            self._access_payload(
                user_id,
                role,
                timedelta(minutes=self.access_minutes),
            ),
            self.secret_key,
            algorithm=self.algorithm,
        )

    def create_refresh_token(self, user_id: int) -> str:
        return jwt.encode(
            self._refresh_payload(
                user_id,
                timedelta(minutes=self.refresh_minutes),
            ),
            self.secret_key,
            algorithm=self.algorithm,
        )  

    def verify(self, token: str, expected: str):
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("token_type") != expected:
                raise HTTPException(status_code=401, detail="Invalid token type")
            return payload
        except InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")