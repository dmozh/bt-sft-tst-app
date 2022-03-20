from sqlalchemy import Column, TEXT
from sqlalchemy.dialects.postgresql import UUID, INTEGER
from sqlalchemy.ext.declarative import declarative_base

DeclarativeBase = declarative_base()


class KeyBody(DeclarativeBase):
    __tablename__ = 'keybody'

    id = Column(UUID, primary_key=True, nullable=False)
    requestkey = Column(TEXT)
    requestbody = Column(TEXT)
    duplicates = Column(INTEGER, nullable=True)


