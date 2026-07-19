from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.authorization import require_authentication
from app.db.session import get_db
from app.schemas.address import AddressCreate, AddressUpdate, AddressResponse
from app.db.models import Address

router = APIRouter(tags=["Addresses"])


@router.get("/addresses", response_model=list[AddressResponse])
def list_addresses(db: Session = Depends(get_db), user = Depends(require_authentication)):
    return db.query(Address).filter(Address.user_id == user.id, Address.deleted_at.is_(None)).order_by(Address.is_default.desc()).all()


@router.post("/addresses", response_model=AddressResponse, status_code=status.HTTP_201_CREATED)
def create_address(payload: AddressCreate, db: Session = Depends(get_db), user = Depends(require_authentication)):
    if payload.is_default:
        db.query(Address).filter(Address.user_id == user.id).update({Address.is_default: False})
    address = Address(user_id=user.id, **payload.model_dump())
    db.add(address)
    db.commit()
    db.refresh(address)
    return address


@router.put("/addresses/{address_id}", response_model=AddressResponse)
def update_address(address_id: int, payload: AddressUpdate, db: Session = Depends(get_db), user = Depends(require_authentication)):
    address = db.query(Address).filter(Address.id == address_id, Address.user_id == user.id, Address.deleted_at.is_(None)).first()
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(address, key, value)
    if payload.is_default:
        db.query(Address).filter(Address.user_id == user.id, Address.id != address_id).update({Address.is_default: False})
    db.commit()
    db.refresh(address)
    return address


@router.delete("/addresses/{address_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_address(address_id: int, db: Session = Depends(get_db), user = Depends(require_authentication)):
    address = db.query(Address).filter(Address.id == address_id, Address.user_id == user.id, Address.deleted_at.is_(None)).first()
    if not address:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Address not found")
    address.deleted_at = datetime.utcnow()
    db.commit()