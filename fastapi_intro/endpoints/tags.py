from fastapi import APIRouter, status, HTTPException, Depends
from pydantic import BaseModel, field_validator, Field
from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from services.database import get_db, AuthorDB

class AuthorCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    country: str | None = Field(default=None, max_length=100)

    @field_validator("name")
    @classmethod
    def strip_whitespaces(cls, v: str) -> str:
        return v.strip()
    
class AuthorUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    country: str | None = Field(default=None, max_length=100)

    @field_validator("name")
    @classmethod
    def strip_whitespaces(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return v.strip()
    
class AuthorPublic(BaseModel):
    id: int
    name: str
    country: str | None

    model_config = {"from_attributes": True}

router = APIRouter(prefix="/authors", tags=["authors"])

def get_author_or_404(author_id: int, db: Session = Depends(get_db)) -> AuthorDB:
    author = db.get(AuthorDB, author_id)
    if author is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No author found with id {author_id}.",
        )
    return author

@router.post("", status_code=status.HTTP_201_CREATED, response_model=AuthorPublic)
def create_author(author: AuthorCreate, db: Session = Depends(get_db)):
    stmt = select(AuthorDB).where(AuthorDB.name == author.name)
    existing = db.scalars(stmt).first()
    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Author '{author.name}' already exists with id {existing.id}.",
        )
    new_author = AuthorDB(**author.model_dump())
    db.add(new_author)
    db.commit()
    db.refresh(new_author)
    return new_author

@router.get("/{author_id}", response_model=AuthorPublic)
def get_author(author: AuthorDB = Depends(get_author_or_404)):
    return author

@router.get("", response_model=list[AuthorPublic])
def list_authors(name: str | None, country: str | None, db: Session = Depends(get_db)):
    stmt = select(AuthorDB)
    if name is not None:
        stmt = stmt.where(AuthorDB.name.like(f"%{name}%"))
    if country is not None:
        stmt = stmt.where(AuthorDB.country == country)
    return db.scalars(stmt).all()

@router.patch("/{author_id}", response_model=AuthorPublic)
def update_author(updates: AuthorUpdate, existing: AuthorDB = Depends(get_author_or_404), db: Session = Depends(get_db)):
    updated_dict = updates.model_dump(exclude_unset=True)
    for field, value in updated_dict.items():
        setattr(existing, field, value)
    db.commit()
    db.refresh(existing)
    return existing

@router.delete("/{author_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_author(existing: AuthorDB = Depends(get_author_or_404), db: Session = Depends(get_db))
    db.delete(existing)
    db.commit()