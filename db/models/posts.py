from sqlalchemy import Column, Integer, ARRAY
from db.models.base import Base


class Posts(Base):
    __tablename__ = 'posts'
    count = Column(Integer, primary_key=True)
    items = Column(ARRAY(Integer))

    def __init__(self, count, items):
        self.count = count
        self.items = items

