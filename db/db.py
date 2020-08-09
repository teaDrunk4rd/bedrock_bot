from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from buttons import Buttons
from config import Config
from db.models.base import Base
from db.models.joke import Joke
from db.models.picture import Picture
from db.models.picture_status import PictureStatus
from db.models.posts import Posts
from db.models.settings import Settings
from db.models.user import User


class DB:
    session = None

    def __init__(self):
        engine = create_engine(Config.db_link, echo=False)
        Session = sessionmaker(bind=engine)
        self.session = Session()
        Base.metadata.create_all(engine, tables=[
            Settings.__table__,
            PictureStatus.__table__,
            Posts.__table__,
            User.__table__,
            Joke.__table__,
            Picture.__table__
        ])
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
                Settings('bot', True),
                Settings('screen', True),
                Settings('user_stats', True),
                Settings('make_joke', True),
                Settings('essay', True),
                Settings('random_post', True),
                Settings('donate', True)
            ])
        if not any(self.session.query(Posts)):  # TODO: or Posts.count != lines.count then update posts and count
            with open('posts.txt', 'r') as f:
                lines = [int(line.strip()) for line in f]
                self.add(Posts(len(lines), lines))
        self.session.commit()

    def __set_consts(self):
        PictureStatus.not_checked = self.session.query(PictureStatus).filter(PictureStatus.key == 'not_checked').first().id
        PictureStatus.confirmed = self.session.query(PictureStatus).filter(PictureStatus.key == 'confirmed').first().id
        PictureStatus.rejected = self.session.query(PictureStatus).filter(PictureStatus.key == 'rejected').first().id

        Settings.bot = self.session.query(Settings).filter(Settings.name == 'bot').first().value == 'true'
        Settings.screen = self.session.query(Settings).filter(Settings.name == 'screen').first().value == 'true'
        Settings.make_joke = self.session.query(Settings).filter(Settings.name == 'make_joke').first().value == 'true'
        Settings.essay = self.session.query(Settings).filter(Settings.name == 'essay').first().value == 'true'
        Settings.random_post = self.session.query(Settings).filter(Settings.name == 'random_post').first().value == 'true'
        Settings.user_stats = self.session.query(Settings).filter(Settings.name == 'user_stats').first().value == 'true'
        Settings.donate = self.session.query(Settings).filter(Settings.name == 'donate').first().value == 'true'

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

    def check_user_current_path(self, user_id, path, in_arg=False):
        if type(path) is dict:  # is button
            path = Buttons.get_key(path)
        return path == self.get_user_path(user_id) if not in_arg else path in self.get_user_path(user_id)


db = DB()
