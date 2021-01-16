from sqlalchemy import Column, Integer, SmallInteger, Boolean, String

from db.models.base import Base


class User(Base):
    __tablename__ = 'users'
    user_id = Column(Integer, primary_key=True)
    apologies_count = Column(SmallInteger, default=0)
    banned = Column(Boolean, default=False)
    path = Column(String, default='')

    def __init__(self, user_id, apologies_count=0, banned=False, path=''):
        self.user_id = user_id
        self.apologies_count = apologies_count
        self.banned = banned
        self.path = path

    def get_status(self):
        if self.banned:
            return 'Забанен'
        elif self.apologies_count > 0:
            return 'Извиняется'
        return 'Активен'
