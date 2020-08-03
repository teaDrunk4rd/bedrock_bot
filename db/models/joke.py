from sqlalchemy import Column, Integer, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship

from db.models.base import Base


class Joke(Base):
    __tablename__ = 'jokes'
    id = Column(Integer, primary_key=True)
    user_id = Column('user_id', Integer, ForeignKey('users.user_id'), nullable=False)
    message_id = Column(String, nullable=False)
    viewed = Column(Boolean, default=False)
    score = Column(Integer, default=0)

    user = relationship('User', backref='jokes')

    def __init__(self, user_id, message_id, viewed=False, score=0):
        self.user_id = user_id
        self.message_id = message_id
        self.viewed = viewed
        self.score = score

