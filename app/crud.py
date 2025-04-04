from datetime import timedelta

from sqlalchemy.orm import Session

from app.models import Contact


def create_contact(db: Session, contact_data, user_id: int):
    existing_contact = db.query(Contact).filter(Contact.email == contact_data.email, Contact.user_id == user_id).first()
    if existing_contact:
        return None
    new_contact = Contact(**contact_data.dict(), user_id=user_id)
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact


def get_contacts(db: Session, skip: int, limit: int, user_id: int):
    return db.query(Contact).filter(Contact.user_id == user_id).offset(skip).limit(limit).all()


def get_contact(db: Session, contact_id: int, user_id: int):
    return db.query(Contact).filter(Contact.id == contact_id, Contact.user_id == user_id).first()


def update_contact(db: Session, contact_id: int, contact_data, user_id: int):
    contact = get_contact(db, contact_id, user_id)
    if contact:
        for key, value in contact_data.dict().items():
            setattr(contact, key, value)
        db.commit()
        db.refresh(contact)
    return contact


def delete_contact(db: Session, contact_id: int, user_id: int):
    contact = get_contact(db, contact_id, user_id)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


def search_contacts(db: Session, first_name, last_name, email, user_id: int):
    query = db.query(Contact).filter(Contact.user_id == user_id)
    if first_name:
        query = query.filter(Contact.first_name.ilike(f"%{first_name}%"))
    if last_name:
        query = query.filter(Contact.last_name.ilike(f"%{last_name}%"))
    if email:
        query = query.filter(Contact.email.ilike(f"%{email}%"))
    return query.all()


def get_upcoming_birthdays(db: Session, user_id: int):
    today = datetime.today().date()
    upcoming = today + timedelta(days=7)
    return db.query(Contact).filter(Contact.user_id == user_id, Contact.birthday >= today,
                                    Contact.birthday <= upcoming).all()
