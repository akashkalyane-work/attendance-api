from fastapi import APIRouter, Depends, Request, Response, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.auth.dependencies import get_current_user
from app.auth.dependencies import AuthServiceDep
from app.auth.schemas import Token

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/login", response_model=Token)
async def login(
    response: Response,
    service: AuthServiceDep,
    form: OAuth2PasswordRequestForm = Depends(),
):
    auth_result = await service.authenticate(form.username, form.password)
    if auth_result is None:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    user_id, role = auth_result

    access, refresh = await service.issue_tokens(user_id, role)

    response.set_cookie(
        key="refresh_token",
        value=refresh,
        httponly=True,
        secure=True,         
        samesite="none",   
        path="/auth/refresh",
    )

    return Token(access_token=access)


@router.post("/refresh", response_model=Token)
async def refresh(
    request: Request,
    response: Response,
    service: AuthServiceDep,
):
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(401, "Missing refresh token")

    access, new_refresh = await service.refresh(refresh_token)

    response.set_cookie(
        key="refresh_token",
        value=new_refresh,
        httponly=True,
        secure=True,          
        samesite="none",      
        path="/auth/refresh",
    )

    return Token(access_token=access)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout(
    response: Response,
    service: AuthServiceDep,
    user=Depends(get_current_user),
):
    await service.logout(user.id)

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token", path="/auth/refresh")
