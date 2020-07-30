from sqlalchemy import Column, Integer, String
from db.models.base import Base


class PictureStatus(Base):
    __tablename__ = 'picture_statuses'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    key = Column(String, nullable=False)

    # TODO: сделать адекватней
    not_checked, checked, rejected = None, None, None

    def __init__(self, name, key):
        self.name = name
        self.key = key

