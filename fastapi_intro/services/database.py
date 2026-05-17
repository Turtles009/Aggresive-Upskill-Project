from sqlalchemy import create_engine, String, Integer, JSON
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Mapped, mapped_column


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


class BookDB(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    author: Mapped[str] = mapped_column(String(200))
    year: Mapped[int] = mapped_column(Integer)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list)
