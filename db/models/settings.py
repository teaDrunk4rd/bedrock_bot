from sqlalchemy import Column, Integer, String
from db.models.base import Base


class Settings(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    value = Column(String, nullable=False)

    def __init__(self, name, value):
        self.name = name
        self.value = value

