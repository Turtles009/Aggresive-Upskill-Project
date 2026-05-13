from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


class Book(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=100)
    year: int = Field(ge=1000)
    tags: list[str] = Field(default_factory=list, max_length=10)


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
    title: str
    author: str
    year: int


router = APIRouter(prefix="/books", tags=["books"])

books_db: dict[int, Book] = {}
next_id = 1


def get_book_or_404(book_id: int) -> Book:
    if book_id not in books_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No book found with id {book_id}.",
        )
    return books_db[book_id]


@router.post("", status_code=status.HTTP_201_CREATED)
def create_book(book: Book):
    global next_id
    books_db[next_id] = book
    current_id = next_id
    next_id += 1
    return {"id": current_id, "book": book}


@router.get("/{book_id}", response_model=BookPublic)
def get_book(book_id: int):
    return get_book_or_404(book_id=book_id)


@router.get("", response_model=list[BookPublic])
def get_books_list(author: str | None = None, year: int | None = None):
    books = list(books_db.values())
    books = [
        book
        for book in books
        if (author is None or book.author == author)
        and (year is None or book.year == year)
    ]
    return books


@router.put("/{book_id}")
def update_book(book_id: int, book: Book):
    get_book_or_404(book_id=book_id)
    books_db[book_id] = book
    return {"id": book_id, "book": book}


@router.patch("/{book_id}")
def patch_book(book_id: int, updates: BookUpdate):
    existing = get_book_or_404(book_id=book_id)
    updated_dict = updates.model_dump(exclude_unset=True)
    updated = existing.model_copy(update=updated_dict)
    books_db[book_id] = updated
    return updated


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(book_id: int):
    get_book_or_404(book_id=book_id)
    del books_db[book_id]
    return {"deleted": book_id}
