from fastapi import APIRouter, status, HTTPException
from pydantic import BaseModel


class Book(BaseModel):
    title: str
    author: str
    year: int
    tags: list[str] = []


class BookPublic(BaseModel):
    title: str
    author: str
    year: int


router = APIRouter(prefix="/books", tags=["books"])

books_db: dict[int, Book] = {}
next_id = 1


@router.post("/books", status_code=status.HTTP_201_CREATED)
def create_book(book: Book):
    global next_id
    books_db[next_id] = book
    current_id = next_id
    next_id += 1
    return {f"Book create at book id: {current_id}"}


@router.get(
    "/books/{book_id}", status_code=status.HTTP_404_NOT_FOUND, response_model=BookPublic
)
def get_book(book_id: int):
    return books_db[book_id]


@router.get("/books", response_model=list[BookPublic])
def get_books_list(author: str | None = None, year: int | None = None):
    books = list(books_db.values())
    books = [
        book
        for book in books
        if (author is None or book.author == author)
        and (year is None or book.year == book.year)
    ]
    return books


@router.put("/books/{book_id}", status_code=status.HTTP_404_NOT_FOUND)
def update_book(book_id: int, updates: dict):
    existing_book = books_db[book_id]
    updated_book = existing_book.model_copy(update=updates)
    books_db[book_id] = updated_book
    return {f"Book updated at book id: {book_id}"}


@router.delete("/books/{book_id}", status_code=status.HTTP_404_NOT_FOUND)
def delete_book(book_id: int):
    if book_id not in books_db:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No book with id: {book_id} found.",
        )
    del books_db[book_id]
    return {"deleted": book_id}
