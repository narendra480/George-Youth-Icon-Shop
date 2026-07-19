from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.db.session import get_db
from app.repositories.user_repository import UserRepository
from app.schemas.response import ApiResponse
from app.schemas.user import UserResponse

router = APIRouter(tags=["Users"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


@router.get("/users/me", response_model=ApiResponse[UserResponse])
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> ApiResponse[UserResponse]:
    user_id = decode_access_token(token)
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalid or expired")
    user = UserRepository(db).get_by_id(int(user_id))
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return ApiResponse(success=True, message="Current user fetched", data=user)
