from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import Config
from db.models.base import Base
from db.models.picture_status import PictureStatus
from db.models.settings import Settings


class DB:
    session = None

    def __init__(self):
        engine = create_engine(Config.db_link, echo=False)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        Base.metadata.create_all(engine)
        self.__run_seeders()

    def __run_seeders(self):
        if not any(self.session.query(PictureStatus)):
            self.session.add_all([
                PictureStatus('Не проверен', 'not_checked'),
                PictureStatus('Проверен', 'checked'),
                PictureStatus('Отвергнут', 'rejected')
            ])
        if not any(self.session.query(Settings)):
            self.session.add_all([
                Settings('bot_on', True),
                Settings('screen', True),
                Settings('user_stats', True),
                Settings('entertain', True),
                Settings('essay', True),
                Settings('classification', True),
                Settings('donate', True)
            ])
        self.session.commit()

    def add(self, entity):
        if type(entity) is list:
            self.session.add_all(entity)
        else:
            self.session.add(entity)
        self.session.commit()  # вроде как есть autocommit

    def update(self, entity, updated_value):
        entity.update(updated_value)
        self.session.commit()


db = DB()
