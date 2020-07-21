from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship

from db.models.base import Base


class Joke(Base):
    __tablename__ = 'jokes'
    id = Column(Integer, primary_key=True)
    user_id = Column('user_id', Integer, ForeignKey('users.user_id'), nullable=False)
    message_id = Column(String, nullable=False)
    viewed = Column(String, default=False)

    user = relationship('User', backref='jokes')

    def __init__(self, user_id, message_id, viewed=False):
        self.user_id = user_id
        self.message_id = message_id
        self.viewed = viewed

