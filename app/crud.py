from datetime import timedelta

from sqlalchemy.orm import Session

from app.models import Contact


def create_contact(db: Session, contact_data, user_id: int):
    """
    Створює новий контакт для вказаного користувача.

    :param db: Сесія бази даних SQLAlchemy
    :param contact_data: Дані нового контакту (Pydantic модель)
    :param user_id: ID поточного користувача
    :return: Створений об'єкт контакту або None, якщо email вже існує
    """
    existing_contact = db.query(Contact).filter(Contact.email == contact_data.email, Contact.user_id == user_id).first()
    if existing_contact:
        return None
    new_contact = Contact(**contact_data.dict(), user_id=user_id)
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact


def get_contacts(db: Session, skip: int, limit: int, user_id: int):
    """
    Отримує список контактів користувача з пагінацією.

    :param db: Сесія бази даних
    :param skip: Кількість пропущених записів
    :param limit: Максимальна кількість результатів
    :param user_id: ID користувача
    :return: Список контактів
    """
    return db.query(Contact).filter(Contact.user_id == user_id).offset(skip).limit(limit).all()


def get_contact(db: Session, contact_id: int, user_id: int):
    """
    Повертає один контакт по його ID для конкретного користувача.

    :param db: Сесія бази даних
    :param contact_id: ID контакту
    :param user_id: ID користувача
    :return: Об'єкт контакту або None
    """
    return db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user_id).first()


def update_contact(db: Session, contact_id: int, contact_data, user_id: int):
    """
    Оновлює контакт користувача за ID.

    :param db: Сесія бази даних
    :param contact_id: ID контакту
    :param contact_data: Нові дані контакту (Pydantic модель)
    :param user_id: ID користувача
    :return: Оновлений контакт або None
    """
    contact = get_contact(db, contact_id, user_id)
    if contact:
        for key, value in contact_data.dict().items():
            setattr(contact, key, value)
        db.commit()
        db.refresh(contact)
    return contact


def delete_contact(db: Session, contact_id: int, user_id: int):
    """
    Видаляє контакт за ID для конкретного користувача.

    :param db: Сесія бази даних
    :param contact_id: ID контакту
    :param user_id: ID користувача
    :return: Видалений контакт або None
    """
    contact = get_contact(db, contact_id, user_id)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


def search_contacts(db: Session, first_name, last_name, email, user_id: int):
    """
    Шукає контакти користувача за іменем, прізвищем або email.

    :param db: Сесія бази даних
    :param first_name: Ім'я для пошуку (опціонально)
    :param last_name: Прізвище для пошуку (опціонально)
    :param email: Email для пошуку (опціонально)
    :param user_id: ID користувача
    :return: Список знайдених контактів
    """
    query = db.query(Contact).filter(Contact.user_id == user_id)
    if first_name:
        query = query.filter(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))
    return query.all()


def get_upcoming_birthdays(db: Session, user_id: int):
    """
    Повертає список контактів, у яких день народження протягом наступних 7 днів.

    :param db: Сесія бази даних
    :param user_id: ID користувача
    :return: Список контактів з близьким днем народження
    """
    today = datetime.today().date()
    upcoming = today + timedelta(days=7)
    return db.query(Contact).filter(Contact.user_id == user_id, Contact.birthday >= today,
                                    Contact.birthday <= upcoming).all()
