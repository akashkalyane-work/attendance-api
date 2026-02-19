from fastapi import APIRouter, Depends, Request, Response, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.dependencies import get_current_user
from app.auth.dependencies import AuthServiceDep
from app.auth.schemas import Token, MobileToken
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login")
async def login(
    request: Request,
    response: Response,
    service: AuthServiceDep,
    form: OAuth2PasswordRequestForm = Depends(),
):
    auth_result = await service.authenticate(form.username, form.password)
    if not auth_result:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id, role = auth_result
    access, refresh = await service.issue_tokens(user_id, role)

    if request.headers.get("x-client-type") == "mobile":
        return MobileToken(
            access_token=access,
            refresh_token=refresh,
        )

    response.set_cookie(
        key="refresh_token",
        value=refresh,
        httponly=True,
        secure=settings.is_production,
        samesite="none" if settings.is_production else "lax",
        path="/auth/refresh",
    )

    return Token(access_token=access)


@router.post("/refresh")
async def refresh(
    request: Request,
    response: Response,
    service: AuthServiceDep,
):
    refresh_token = request.cookies.get("refresh_token")
    is_web = True

    if not refresh_token:
        is_web = False
        auth = request.headers.get("Authorization")
        if auth and auth.startswith("Bearer "):
            refresh_token = auth.split(" ")[1]

    if not refresh_token:
        raise HTTPException(status_code=401, detail="Missing refresh token")

    access, new_refresh = await service.refresh(refresh_token)

    if is_web:
        response.set_cookie(
            key="refresh_token",
            value=new_refresh,
            httponly=True,
            secure=settings.is_production,
            samesite="none" if settings.is_production else "lax",
            path="/auth/refresh",
        )
        return Token(access_token=access)

    return {
        "access_token": access,
        "refresh_token": new_refresh,
        "token_type": "bearer",
    }


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    service: AuthServiceDep,
    user=Depends(get_current_user),
):
    await service.logout(user.id)

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token", path="/auth/refresh")
