import datetime
import os

from dotenv import load_dotenv
from sqlalchemy import (Boolean, Column, DateTime, ForeignKey, Integer, String,
                        create_engine)
from sqlalchemy.orm import DeclarativeBase, relationship

load_dotenv()

host = str(os.getenv("POSTGRES_HOST"))
password = str(os.getenv("POSTGRES_PASSWORD"))
database = str(os.getenv("POSTGRES_DB"))

engine = create_engine(f"postgresql+psycopg2://postgres:{password}@{host}/{database}")


class Base(DeclarativeBase):
    pass


class Law(Base):
    __tablename__ = "Laws"
    id = Column(Integer, primary_key=True)
    law_name = Column(String)
    law_number = Column(String)
    terms = relationship("Term", back_populates="law")
    number_of_mentions = Column(Integer, default=1)
    is_valid = Column(String)
    date_created = Column(DateTime, default=datetime.datetime.utcnow)


class Term(Base):
    __tablename__ = "Terms"
    id = Column(Integer, primary_key=True)
    term_name = Column(String)
    definition = Column(String)
    law_name = Column(String)
    law_id = Column(Integer, ForeignKey("Laws.id"))
    law = relationship("Law", back_populates="terms")
    date_created = Column(DateTime, default=datetime.datetime.utcnow)


Base.metadata.create_all(bind=engine)
