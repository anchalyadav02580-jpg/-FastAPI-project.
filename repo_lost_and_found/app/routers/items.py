"""
API routes for lost/found items.
"""

from typing import List

from fastapi import APIRouter, HTTPException, Depends, status as http_status
from sqlmodel import Session, select

from app.database import get_session
from app.models import Item, ItemCreate, ItemUpdate, ItemStatus, ItemCategory

router = APIRouter(prefix="/items", tags=["Items"])


@router.post("", response_model=Item, status_code=http_status.HTTP_201_CREATED)
def create_item(item: ItemCreate, session: Session = Depends(get_session)):
    """Create a new lost/found item report."""
    db_item = Item(**item.model_dump())
    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.get("", response_model=List[Item])
def read_items(session: Session = Depends(get_session)):
    """Return all reported items."""
    return session.exec(select(Item)).all()


@router.get("/status/{item_status}", response_model=List[Item])
def read_items_by_status(item_status: ItemStatus, session: Session = Depends(get_session)):
    """Return all items with the given status (Lost, Found, Returned)."""
    return session.exec(select(Item).where(Item.status == item_status)).all()


@router.get("/category/{item_category}", response_model=List[Item])
def read_items_by_category(item_category: ItemCategory, session: Session = Depends(get_session)):
    """Return all items belonging to a particular category."""
    return session.exec(select(Item).where(Item.category == item_category)).all()


@router.get("/{item_id}", response_model=Item)
def read_item(item_id: int, session: Session = Depends(get_session)):
    """Return a single item by ID, or 404 if it doesn't exist."""
    item = session.get(Item, item_id)
    if not item:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=f"Item with id {item_id} not found")
    return item


@router.put("/{item_id}", response_model=Item)
def update_item(item_id: int, item_update: ItemUpdate, session: Session = Depends(get_session)):
    """Update an existing item's details/status. Only supplied fields change."""
    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=f"Item with id {item_id} not found")

    update_data = item_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_item, key, value)

    session.add(db_item)
    session.commit()
    session.refresh(db_item)
    return db_item


@router.delete("/{item_id}", status_code=http_status.HTTP_204_NO_CONTENT)
def delete_item(item_id: int, session: Session = Depends(get_session)):
    """Delete an item report by ID."""
    db_item = session.get(Item, item_id)
    if not db_item:
        raise HTTPException(status_code=http_status.HTTP_404_NOT_FOUND, detail=f"Item with id {item_id} not found")
    session.delete(db_item)
    session.commit()
    return None
