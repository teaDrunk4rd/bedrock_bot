from sqlalchemy import Column, Integer, String
from db.models.base import Base


class Settings(Base):
    __tablename__ = 'settings'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    value = Column(String, nullable=False)

    bot, make_joke, user_stats, essay, random_post, call_admin, donate = None, None, None, None, None, None, None

    def __init__(self, name, value):
        self.name = name
        self.value = value

    @staticmethod
    def get(str_field):
        return getattr(Settings, str_field)

    @staticmethod
    def change(str_field):
        setattr(Settings, str_field, not Settings.get(str_field))
