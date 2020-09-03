from sqlalchemy import Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from db.models.base import Base


class Picture(Base):
    __tablename__ = 'pictures'
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    status_id = Column(Integer, ForeignKey('picture_statuses.id'), nullable=False)
    url = Column(String, nullable=False)
    name = Column(String, nullable=False)
    message_id = Column(String, nullable=False)
    comment = Column(String, nullable=True)
    inspector_id = Column(Integer, ForeignKey('users.user_id'), nullable=True)

    user = relationship('User', backref='pictures', foreign_keys=user_id)
    status = relationship('PictureStatus', backref='pictures')
    inspector = relationship('User', backref='pictures_inspected', foreign_keys=inspector_id)

    def __init__(self, user_id, status_id, url, name, message_id, comment=None):
        self.user_id = user_id
        self.status_id = status_id
        self.url = url
        self.name = name
        self.message_id = message_id
        self.comment = comment

