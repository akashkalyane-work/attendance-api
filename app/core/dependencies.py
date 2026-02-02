from typing import Annotated

from fastapi import Depends, HTTPException, status

from app.auth.dependencies import get_current_user
from app.core.enums import UserRole
from app.users.models import User


# def require_admin(user: User = Depends(get_current_user)):
# def require_admin():
    # if user.role != "ADMIN":
    #     raise HTTPException(
    #         status_code=status.HTTP_403_FORBIDDEN,
    #         detail="Admin access required"
    #     )
    # return "ADMIN"

def require_admin(
    user: Annotated[User, Depends(get_current_user)],
):
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user