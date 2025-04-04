from fastapi import APIRouter, HTTPException, Form, status, BackgroundTasks

from app.schemas import UserCreate, Token, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()
auth_service = AuthService()


# Реєстрація користувача з поверненням 201 Created та відправкою листа верифікації
@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, background_tasks: BackgroundTasks):
    new_user = auth_service.register_user(user)
    await auth_service.send_verification_email(new_user, background_tasks)
    return new_user


# Логін користувача через передачу username та password у тілі запиту
@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(username: str = Form(...), password: str = Form(...)):
    db_user = auth_service.find_user_by_email(username)
    if not db_user or not auth_service.verify_password(password, db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    access_token = auth_service.create_access_token({"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# Верифікація користувача через посилання
@router.get("/verify-email/{token}")
def verify_email(token: str):
    return auth_service.verify_email(token)
