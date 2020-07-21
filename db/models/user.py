from sqlalchemy import Column, Integer, SmallInteger, Boolean
from db.models.base import Base


class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    apologies_count = Column(SmallInteger, default=0)
    banned = Column(Boolean, default=False)
    scores = Column(Integer, default=0)

    def __init__(self, user_id, apologies_count=0, banned=False, scores=0):
        self.user_id = user_id
        self.apologies_count = apologies_count
        self.banned = banned
        self.scores = scores

