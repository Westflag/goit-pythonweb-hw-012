from fastapi import APIRouter, Depends, UploadFile, File, status

from app.dependencies import get_current_user
from app.schemas import UserResponse
from app.services.auth_service import AuthService
from app.services.rate_limiter import limit_requests

router = APIRouter()
auth_service = AuthService()


@router.get("/me", response_model=UserResponse, dependencies=[Depends(limit_requests)])
def get_me(current_user=Depends(get_current_user)):
    return current_user


@router.post("/avatar", status_code=status.HTTP_201_CREATED)
def update_avatar(current_user=Depends(get_current_user), file: UploadFile = File(...)):
    file_bytes = file.file.read()
    return auth_service.upload_avatar_to_cloudinary(current_user, file_bytes)
