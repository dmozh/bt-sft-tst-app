from sqlalchemy import Column, TEXT
from sqlalchemy.dialects.postgresql import UUID, INTEGER
from sqlalchemy.ext.declarative import declarative_base

DeclarativeBase = declarative_base()


class Duplicates(DeclarativeBase):
    __tablename__ = 'duplicates'

    id = Column(UUID, primary_key=True, nullable=False)
    requestkey = Column(TEXT)
    duplicates = Column(INTEGER, nullable=True)


