import os
from datetime import datetime, timedelta

import cloudinary
import cloudinary.uploader
from fastapi import BackgroundTasks
from fastapi import HTTPException
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig
from jose import jwt, JWSError, JWTError
from passlib.context import CryptContext
from pydantic import SecretStr
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("EMAIL_USER", "api"),
    MAIL_PASSWORD=os.getenv("EMAIL_PASSWORD", SecretStr('eab9f8d8e7ab19d53c529b72c7445fdd')),
    MAIL_FROM=os.getenv("EMAIL_FROM", "test@test.com"),
    MAIL_PORT=int(os.getenv("EMAIL_PORT", "587")),
    MAIL_SERVER=os.getenv("EMAIL_HOST", "live.smtp.mailtrap.io"),
    MAIL_FROM_NAME="Contacts App",
    MAIL_STARTTLS=True,
    MAIL_SSL_TLS=False,
)

SECRET_KEY = os.getenv("SECRET_KEY", "secret")
ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Cloudinary configuration
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)


class AuthService:
    """
   Сервіс для автентифікації користувачів, генерації JWT токенів, верифікації електронної пошти,
   хешування паролів, керування аватарами через Cloudinary.
   """
    # Створення JWT access token
    def create_access_token(self, data: dict, expires_delta: timedelta = timedelta(hours=1)):
        """Створює JWT токен доступу."""
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    # Хешування пароля
    def get_password_hash(self, password: str) -> str:
        """Хешує пароль користувача."""
        return pwd_context.hash(password)

    # Перевірка пароля
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Перевіряє, чи відповідає введений пароль хешу."""
        return pwd_context.verify(plain_password, hashed_password)

    # Пошук користувача по email
    def find_user_by_email(self, email: str, db: Session = next(get_db())):
        """Повертає користувача за email."""
        return db.query(User).filter(User.email == email).first()

    # Реєстрація нового користувача
    def register_user(self, user_data, db: Session = next(get_db())):
        """Реєструє нового користувача з хешованим паролем."""
        existing = db.query(User).filter(User.email == user_data.email).first()
        if existing:
            raise HTTPException(status_code=409, detail="User with this email already exists.")
        hashed_password = self.get_password_hash(user_data.password)
        new_user = User(email=user_data.email, password=hashed_password, is_verified=False)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    # Надсилання листа з посиланням для верифікації email
    async def send_verification_email(self, user, background_tasks: BackgroundTasks):
        """Надсилає верифікаційний email користувачу з посиланням на підтвердження."""
        token = self.create_access_token({"sub": user.email})
        verification_link = f"{os.getenv('FRONTEND_URL')}/verify-email/{token}"
        message = MessageSchema(
            subject="Verify your email",
            recipients=[user.email],
            body=f"Hello {user.email}, please verify your email by clicking the link: {verification_link}",
            subtype="plain"
        )
        fm = FastMail(conf)
        def _safe_send_email():
            try:
                return fm.send_message(message)
            except Exception as e:
                # Тут можна використати logger.error
                print(f"❌ Failed to send email: {e}")
                return None

        background_tasks.add_task(_safe_send_email)




    # Підтвердження email користувача
    def verify_email(self, token: str, db: Session = next(get_db())):
        """Підтверджує електронну пошту користувача за токеном."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload.get("sub")
            user = db.query(User).filter(User.email == email).first()
            if user:
                user.is_verified = True
                db.commit()
                return {"detail": "Email verified successfully"}
            else:
                raise HTTPException(status_code=404, detail="User not found")
        except JWSError:
            raise HTTPException(status_code=400, detail="Invalid verification token")

    # Завантаження аватара користувача на Cloudinary
    def upload_avatar_to_cloudinary(self, current_user, file_bytes, db: Session = next(get_db())):
        """
     Завантажує аватар користувача на Cloudinary і зберігає URL в базі.

     :param current_user: Поточний користувач
     :param file_bytes: Бінарні дані файлу
     :param db: Сесія бази даних
     :return: Словник з URL до аватару
     """
        result = cloudinary.uploader.upload(file_bytes, folder="avatars")
        user = db.query(User).filter(User.id == current_user.id).first()
        user.avatar_url = result["secure_url"]
        db.commit()
        return {"avatar_url": result["secure_url"]}

    async def send_password_reset_email(self, email: str, background_tasks: BackgroundTasks,
                                        db: Session = next(get_db())):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return  # Не розкриваємо, що email не знайдено

        token = self.create_access_token({"sub": user.email})
        reset_link = f"{os.getenv('FRONTEND_URL')}/reset-password?token={token}"

        message = MessageSchema(
            subject="Password Reset",
            recipients=[user.email],
            body=f"Click to reset your password: {reset_link}",
            subtype="plain"
        )
        fm = FastMail(conf)

        def _safe_send_email():
            try:
                return fm.send_message(message)
            except Exception as e:
                # Тут можна використати logger.error
                print(f"❌ Failed to send email: {e}")
                return None

        background_tasks.add_task(_safe_send_email)


    def reset_password(self, token: str, new_password: str, db: Session = next(get_db())):
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email = payload.get("sub")
        except JWTError:
            raise HTTPException(status_code=400, detail="Invalid token")

        user = db.query(User).filter(User.email == email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        user.password = self.get_password_hash(new_password)
        db.commit()
