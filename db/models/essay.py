from sqlalchemy import Column, Integer, ForeignKey, String, Boolean
from sqlalchemy.orm import relationship

from db.models.base import Base


class Essay(Base):
    __tablename__ = 'essay'
    id = Column(Integer, primary_key=True)
    user_id = Column('user_id', Integer, ForeignKey('users.user_id'), nullable=False)
    message_id = Column(String, nullable=False)
    text = Column(String, nullable=False)
    processed_text = Column(String, nullable=True)

    user = relationship('User', backref='essay')

    def __init__(self, user_id, message_id, text, processed_text=None):
        self.user_id = user_id
        self.message_id = message_id
        self.text = text
        self.processed_text = processed_text
