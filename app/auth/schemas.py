from pydantic import BaseModel


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class MobileToken(Token):
    refresh_token: str


class RefreshTokenRequest(BaseModel):
    refresh_token: str