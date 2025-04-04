from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import models, database
from app.routers import contacts, auth, users

# Ініціалізація бази даних за допомогою ORM SQLAlchemy
models.Base.metadata.create_all(bind=database.engine)

# Ініціалізація FastAPI з автоматичною генерацією Swagger документації
app = FastAPI(
    title="Contact Management API",
    description="API з підтримкою аутентифікації, авторизації, роботи з контактами, аватарами та верифікацією email.",
    version="2.0.0"
)

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["Auth"])
app.include_router(users.router, prefix="/api/v1/users", tags=["Users"])
app.include_router(contacts.router, prefix="/api/v1/contacts", tags=["Contacts"])
