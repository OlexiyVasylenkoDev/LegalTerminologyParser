import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

load_dotenv()

host = str(os.getenv("POSTGRES_HOST"))
password = str(os.getenv("POSTGRES_PASSWORD"))
database = str(os.getenv("POSTGRES_DB"))

engine = create_engine(f"postgresql+psycopg2://postgres:{password}@{host}/{database}")


class Base(DeclarativeBase):
    pass


class Law(Base):
    __tablename__ = "Laws"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str]
    terms: Mapped[str]
    references: Mapped[int]


class Term(Base):
    __tablename__ = "Terms"
    id: Mapped[int] = mapped_column(primary_key=True)
    content: Mapped[str]
    law: Mapped[str]


Base.metadata.create_all(bind=engine)
