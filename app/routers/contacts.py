from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import schemas, crud, database
from app.dependencies import get_current_user

router = APIRouter(prefix="/contacts")


@router.post("/", response_model=schemas.ContactResponse, status_code=status.HTTP_201_CREATED)
def create_contact(contact: schemas.ContactCreate, db: Session = Depends(database.get_db),
                   current_user=Depends(get_current_user)):
    created_contact = crud.create_contact(db, contact, current_user.id)
    if created_contact is None:
        raise HTTPException(status_code=400, detail="Contact with this email already exists.")
    return created_contact

@router.get("/", response_model=List[schemas.ContactResponse])
def read_contacts(skip: int = 0, limit: int = 10, db: Session = Depends(database.get_db),
                  current_user=Depends(get_current_user)):
    return crud.get_contacts(db, skip, limit, current_user.id)

@router.get("/{contact_id:int}", response_model=schemas.ContactResponse)
def read_contact(contact_id: int, db: Session = Depends(database.get_db), current_user=Depends(get_current_user)):
    contact = crud.get_contact(db, contact_id, current_user.id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.put("/{contact_id:int}", response_model=schemas.ContactResponse)
def update_contact(contact_id: int, contact: schemas.ContactCreate, db: Session = Depends(database.get_db),
                   current_user=Depends(get_current_user)):
    db_contact = crud.update_contact(db, contact_id, contact, current_user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return db_contact

@router.delete("/{contact_id:int}")
def delete_contact(contact_id: int, db: Session = Depends(database.get_db), current_user=Depends(get_current_user)):
    db_contact = crud.delete_contact(db, contact_id, current_user.id)
    if db_contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return {"detail": "Contact deleted"}

@router.get("/search", response_model=List[schemas.ContactResponse])
def search_contacts(
        first_name: Optional[str] = Query(default=None),
        last_name: Optional[str] = Query(default=None),
        email: Optional[str] = Query(default=None),
        db: Session = Depends(database.get_db),
        current_user=Depends(get_current_user)
):
    return crud.search_contacts(db, first_name, last_name, email, current_user.id)

@router.get("/upcoming-birthdays", response_model=List[schemas.ContactResponse])
def upcoming_birthdays(db: Session = Depends(database.get_db), current_user=Depends(get_current_user)):
    return crud.get_upcoming_birthdays(db, current_user.id)
