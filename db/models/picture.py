from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from db.models.base import Base


class Picture(Base):
    __tablename__ = 'pictures'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    status_id = Column(Integer, ForeignKey('picture_statuses.id'), nullable=False)
    photo_link = Column(String, nullable=False)
    message_id = Column(String, nullable=False)
    comment = Column(String, nullable=True)

    user = relationship('User', backref='pictures')
    status = relationship('PictureStatus', backref='pictures')

    def __init__(self, user_id, status_id, photo_link, message_id, comment=None):
        self.user_id = user_id
        self.status_id = status_id
        self.photo_link = photo_link
        self.message_id = message_id
        self.comment = comment

