from sqlalchemy import create_engine, String, Integer, JSON, ForeignKey, Table, Column
from sqlalchemy.orm import (
    DeclarativeBase,
    sessionmaker,
    Mapped,
    mapped_column,
    relationship,
)


Database_URL = "postgresql://postgres:devpassword@localhost:5432/booksdb"

engine = create_engine(Database_URL, echo=True)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class AuthorDB(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    country: Mapped[str | None] = mapped_column(String(200), nullable=True)

    books: Mapped[list["BookDB"]] = relationship(back_populates="author")


book_tags = Table(
    "book_tags",
    Base.metadata,
    Column("book_id", ForeignKey("books.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class TagDB(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    books: Mapped[list["BookDB"]] = relationship(
        secondary=book_tags, back_populates="tags"
    )


class BookDB(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    year: Mapped[int] = mapped_column(Integer)

    author_id: Mapped[int] = mapped_column(ForeignKey("authors.id"))

    author: Mapped["AuthorDB"] = relationship(back_populates="books")
    tags: Mapped[list["TagDB"]] = relationship(
        secondary=book_tags, back_populates="books"
    )
