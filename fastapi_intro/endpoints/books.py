from fastapi import APIRouter, status, HTTPException, Depends, Header
from pydantic import BaseModel, Field, field_validator
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload, joinedload
from services.database import get_db, BookDB, AuthorDB, TagDB


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


class AuthorPublic(BaseModel):
    id: int
    name: str
    country: str | None = None

    model_config = {"from_attributes": True}


class TagPublic(BaseModel):
    id: int
    name: str

    model_config = {"from_attributes": True}


class BookPublic(BaseModel):
    id: int
    title: str
    year: int
    author: AuthorPublic
    tags: list[TagPublic]

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


def get_or_create_author(db: Session, name: str) -> AuthorDB:
    stmt = select(AuthorDB).where(AuthorDB.name == name)
    author = db.scalars(stmt).first()
    if author is None:
        author = AuthorDB(name=name)
        db.add(author)
        db.flush()
    return author


def get_or_create_tags(db: Session, tag_names: list[str]) -> list[TagDB]:
    if not tag_names:
        return []
    stmt = select(TagDB).where(TagDB.name.in_(tag_names))
    existing = list(db.scalars(stmt).all())
    existing_names = {tag.name for tag in existing}
    new_names = [name for name in tag_names if name not in existing_names]
    new_tags = [TagDB(name=name) for name in new_names]
    for tag in new_tags:
        db.add(tag)
    if new_tags:
        db.flush()
    return existing + new_tags


@router.post("", status_code=status.HTTP_201_CREATED, response_model=BookPublic)
def create_book(
    book: Book,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user),
):
    print(f"User {user_id} is creating a book.")

    author = get_or_create_author(db, book.author)
    tags = get_or_create_tags(db, book.tags)

    new_book = BookDB(
        title=book.title,
        year=book.year,
        author=author,
        tags=tags,
    )
    db.add(new_book)
    db.commit()
    db.refresh(new_book)
    return new_book


@router.get("/{book_id}", response_model=BookPublic)
def get_book(book_id: int, db: Session = Depends(get_db)):
    stmt = (
        select(BookDB)
        .where(BookDB.id == book_id)
        .options(
            joinedload(BookDB.author),
            selectinload(BookDB.tags),
        )
    )
    book = db.scalars(stmt).first()
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No book found for id {book_id}.",
        )
    return book


@router.get("", response_model=list[BookPublic])
def get_books_list(
    pg: PaginationParams = Depends(pagination),
    author: str | None = None,
    year: int | None = None,
    db: Session = Depends(get_db),
):
    stmt = select(BookDB).options(joinedload(BookDB.author), selectinload(BookDB.tags))
    if author is not None:
        stmt = stmt.join(AuthorDB).where(AuthorDB.name == author)
    if year is not None:
        stmt = stmt.where(BookDB.year == year)
    stmt = stmt.offset(pg.offset).limit(pg.limit)
    return db.scalars(stmt).unique().all()


@router.put("/{book_id}", response_model=BookPublic)
def update_book(
    book_id: int,
    new_book: Book,
    db: Session = Depends(get_db),
):
    existing = db.get(BookDB, book_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No book found with id {book_id}",
        )
    existing.title = new_book.title
    existing.year = new_book.year
    existing.author = get_or_create_author(db, new_book.author)
    existing.tags = get_or_create_tags(db, new_book.tags)

    db.commit()
    db.refresh(existing)
    return existing


@router.patch("/{book_id}", response_model=BookPublic)
def patch_book(
    book_id: int,
    updates: BookUpdate,
    db: Session = Depends(get_db),
):
    existing = db.get(BookDB, book_id)

    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No book found with id {book_id}",
        )

    updated_dict = updates.model_dump(exclude_unset=True)
    if "title" in updated_dict:
        existing.title = updated_dict["title"]
    if "year" in updated_dict:
        existing.year = updated_dict["year"]
    if "author" in updated_dict:
        existing.author = get_or_create_author(db, updated_dict["author"])
    if "tags" in updated_dict:
        existing.tags = get_or_create_tags(db, updated_dict["tags"])

    db.commit()
    db.refresh(existing)
    return existing


@router.delete("/{book_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_book(
    book_id: int,
    db: Session = Depends(get_db),
):
    existing = db.get(BookDB, book_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No book found with id {book_id}",
        )
    db.delete(existing)
    db.commit()
