from typing import Optional

from fastapi import Request, HTTPException, status
from fastapi.security import OAuth2
from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.security.utils import get_authorization_scheme_param


class OAuth2PasswordBearerWithCookie(OAuth2):
    def __init__(self, tokenUrl: str, auto_error: bool = True):
        flows = OAuthFlowsModel(password={"tokenUrl": tokenUrl})
        super().__init__(flows=flows, auto_error=auto_error)

    async def __call__(self, request: Request) -> Optional[str]:
        token = request.cookies.get("access_token")
        if token:
            return token

        auth = request.headers.get("Authorization")
        scheme, param = get_authorization_scheme_param(auth)

        if not auth or scheme.lower() != "bearer":
            if self.auto_error:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Not authenticated",
                )
            return None

        return param