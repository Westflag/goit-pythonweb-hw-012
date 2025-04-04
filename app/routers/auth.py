from fastapi import APIRouter, HTTPException, Form, status, BackgroundTasks

from app.schemas import UserCreate, Token, UserResponse
from app.services.auth_service import AuthService

router = APIRouter()
auth_service = AuthService()


# Реєстрація користувача з поверненням 201 Created та відправкою листа верифікації
@router.post("/signup", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, background_tasks: BackgroundTasks):
    """
    Реєстрація нового користувача.

    - **user**: Дані нового користувача
    - **background_tasks**: Завдання у фоновому режимі для надсилання верифікації
    - **db**: Сесія бази даних

    :return: Дані нового користувача з відповіддю 201 Created
    """
    new_user = auth_service.register_user(user)
    await auth_service.send_verification_email(new_user, background_tasks)
    return new_user


# Логін користувача через передачу username та password у тілі запиту
@router.post("/login", response_model=Token, status_code=status.HTTP_200_OK)
def login(username: str = Form(...), password: str = Form(...)):
    """
    Авторизація користувача та видача JWT токена.

    - **form_data**: Логін і пароль
    - **db**: Сесія бази даних

    :return: JWT токен доступу (access_token)
    """
    db_user = auth_service.find_user_by_email(username)
    if not db_user or not auth_service.verify_password(password, db_user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    access_token = auth_service.create_access_token({"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer"}


# Верифікація користувача через посилання
@router.get("/verify-email/{token}")
def verify_email(token: str):
    """
    Підтвердження електронної пошти користувача.

    - **token**: Токен підтвердження з листа
    - **db**: Сесія бази даних

    :return: Результат верифікації email
    """
    return auth_service.verify_email(token)
