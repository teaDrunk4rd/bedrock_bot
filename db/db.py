from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from buttons import Buttons
from config import Config
from db.models.base import Base
from db.models.joke import Joke
from db.models.picture import Picture
from db.models.picture_status import PictureStatus
from db.models.settings import Settings
from db.models.user import User


class DB:
    session = None

    def __init__(self):
        engine = create_engine(Config.db_link, echo=False)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        Base.metadata.create_all(engine, tables=[User.__table__, Joke.__table__, Picture.__table__])
        self.__run_seeders()
        self.__set_consts()

    def __run_seeders(self):
        if not any(self.session.query(PictureStatus)):
            self.add([
                PictureStatus('Не проверен', 'not_checked'),
                PictureStatus('Принят', 'confirmed'),
                PictureStatus('Отклонен', 'rejected')
            ])
        if not any(self.session.query(Settings)):
            self.add([
                Settings('bot_on', True),
                Settings('screen', True),
                Settings('user_stats', True),
                Settings('entertain', True),
                Settings('essay', True),
                Settings('classification', True),
                Settings('donate', True)
            ])
        self.session.commit()

    def __set_consts(self):
        PictureStatus.not_checked = self.session.query(PictureStatus).filter(PictureStatus.key == 'not_checked').first().id
        PictureStatus.confirmed = self.session.query(PictureStatus).filter(PictureStatus.key == 'confirmed').first().id
        PictureStatus.rejected = self.session.query(PictureStatus).filter(PictureStatus.key == 'rejected').first().id

        Settings.bot_on = self.session.query(Settings).filter(Settings.name == 'bot_on').first().value
        Settings.screen = self.session.query(Settings).filter(Settings.name == 'screen').first().value
        Settings.user_stats = self.session.query(Settings).filter(Settings.name == 'user_stats').first().value
        Settings.entertain = self.session.query(Settings).filter(Settings.name == 'entertain').first().value
        Settings.essay = self.session.query(Settings).filter(Settings.name == 'essay').first().value
        Settings.classification = self.session.query(Settings).filter(Settings.name == 'classification').first().value
        Settings.donate = self.session.query(Settings).filter(Settings.name == 'donate').first().value

    def add(self, entity):
        if type(entity) is list:
            self.session.add_all(entity)
        else:
            self.session.add(entity)
        self.session.commit()  # вроде как есть autocommit

    def update(self, entity, updated_value):
        entity.update(updated_value)
        self.session.commit()

    def get_user(self, user_id):
        user = self.session.query(User).filter(User.user_id == user_id)
        if not user.first():
            self.add(User(user_id))
        return user

    def get_user_path(self, user_id):
        user = self.get_user(user_id).first()
        return user.path

    def check_user_current_path(self, user_id, path):
        if type(path) is dict:  # is button
            path = Buttons.get_key(path)
        return self.get_user_path(user_id) == path


db = DB()
