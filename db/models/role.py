from sqlalchemy import Column, Integer, String
from db.models.base import Base


class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    key = Column(String, nullable=False)

    admin, editor, user = None, None, None

    def __init__(self, name, key):
        self.name = name
        self.key = key

