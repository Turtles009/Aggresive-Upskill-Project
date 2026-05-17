from fastapi import APIRouter, status, HTTPException, Depends, Header
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session
from services.database import get_db, BookDB


class Book(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=100)
    year: int = Field(ge=1000)
    tags: list[str] = Field(default_factory=list, max_length=10)

    @field_validator("year")
    @classmethod
    def year_not_in_future(cls, v: int | None) -> int | None:
        if v is None:
            return v
        current_year = datetime.now().year
        if v > current_year:
            raise ValueError(
                f"year cannot be in the future (current year : {current_year})"
            )
        return v

    @field_validator("tags")
    @classmethod
    def tags_lowercase(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v
        return [tag.lower() for tag in v]

    @field_validator("title", "author")
    @classmethod
    def strip_whitespace(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return v.strip()


class BookUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    author: str | None = Field(default=None, min_length=1, max_length=100)
    year: int | None = Field(default=None, ge=1000)
    tags: list[str] | None = Field(default=None, max_length=10)

    @field_validator("year")
    @classmethod
    def year_not_in_future(cls, v: int | None) -> int | None:
        if v is None:
            return v
        current_year = datetime.now().year
        if v > current_year:
            raise ValueError(
                f"year cannot be in the future (current year : {current_year})"
            )
        return v

    @field_validator("tags")
    @classmethod
    def tags_lowercase(cls, v: list[str] | None) -> list[str] | None:
        if v is None:
            return v
        return [tag.lower() for tag in v]

    @field_validator("title", "author")
    @classmethod
    def strip_whitespace(cls, v: str | None) -> str | None:
        if v is None:
            return v
        return v.strip()


class BookPublic(BaseModel):
    id: int
    title: str
    author: str
    year: int

    model_config = {"from_attributes": True}


class PaginationParams(BaseModel):
    limit: int = Field(default=10, ge=1, le=100)
    offset: int = Field(default=0, ge=0)


router = APIRouter(prefix="/books", tags=["books"])


def get_book_or_404(book_id: int, db: Session = Depends(get_db)) -> BookDB:
    book = db.get(BookDB, book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No book found with id {book_id}.",
        )
    return book


def pagination(limit: int = 10, offset: int = 0) -> PaginationParams:
    return PaginationParams(limit=limit, offset=offset)


def get_current_user(x_user_id: str | None = Header(default=None)):
    if x_user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Missing x_user_id header"
        )
    return x_user_id


@router.post("", status_code=status.HTTP_201_CREATED, response_model=BookPublic)
def create_book(
    book: Book,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    print(f"User {user_id} is creating a book.")
    new_book = BookDB(**book.model_dump())
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


@router.get("/{book_id}", response_model=BookPublic)
def get_book(book: BookDB = Depends(get_book_or_404)):
    return book


@router.get("", response_model=list[BookPublic])
def get_books_list(
    pg: PaginationParams = Depends(pagination),
    author: str | None = None,
    year: int | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(BookDB)
    if author is not None:
        stmt = stmt.where(BookDB.author == author)
    if year is not None:
        stmt = stmt.where(BookDB.year == year)
    stmt = stmt.offset(pg.offset).limit(pg.limit)
    return db.scalars(stmt).all()


@router.put("/{book_id}", response_model=BookPublic)
def update_book(
    book_id: int,
    new_book: Book,
    existing: BookDB = Depends(get_book_or_404),
    db: Session = Depends(get_db),
):
    for field, value in new_book.model_dump().items():
        setattr(existing, field, value)
    db.commit()
    db.refresh(existing)
    return existing


@router.patch("/{book_id}", response_model=BookPublic)
def patch_book(
    book_id: int,
    updates: BookUpdate,
    existing: BookDB = Depends(get_book_or_404),
    db: Session = Depends(get_db),
):
    updated_dict = updates.model_dump(exclude_unset=True)
    for field, value in updated_dict.items():
        setattr(existing, field, value)
    db.commit()
    db.refresh(existing)
    return existing


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    existing: BookDB = Depends(get_book_or_404),
    db: Session = Depends(get_db),
):
    db.delete(existing)
    db.commit()
