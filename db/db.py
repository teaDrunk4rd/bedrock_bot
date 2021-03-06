import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from config import Config
from db.models.base import Base
from db.models.joke import Joke
from db.models.posts import Posts
from db.models.settings import Settings
from db.models.user import User
from db.models.essay import Essay
from sqlalchemy.inspection import inspect

location = '\\'.join(os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__))).split('\\')[:-1])


class DB:
    session = None

    def __init__(self, run_seeders=False):
        engine = create_engine(Config.db_link, echo=False)  # TODO: db backups
        self.session = scoped_session(sessionmaker(bind=engine))()
        if run_seeders:
            Base.metadata.create_all(engine, tables=[
                Settings.__table__,
                Posts.__table__,
                User.__table__,
                Joke.__table__,
                Essay.__table__
            ])
            self.__run_seeders()
            self.__set_consts()

    def __del__(self):
        self.session.close()

    def __run_seeders(self):
        settings = [
            Settings('bot', True),
            Settings('user_stats', True),
            Settings('make_joke', True),
            Settings('essay', True),
            Settings('random_post', True),
            Settings('call_admin', True),
            Settings('donate', True),
        ]
        for setting in settings:
            if not any(self.session.query(Settings).filter(Settings.name == setting.name)):
                self.add(setting)

        with open(os.path.join(location, 'posts.txt'), 'r', encoding='utf-8') as f:
            lines = [int(line.strip()) for line in f]
        posts = self.session.query(Posts).first()
        if not posts:
            self.add(Posts(len(lines), lines))
        elif posts.count != len(lines):
            posts.count = len(lines)
            posts.items = lines

        for admin_id in Config.admin_ids:
            if not self.session.query(User).filter(User.user_id == admin_id).first():
                self.add(User(admin_id))
        self.session.commit()

    def __set_consts(self):
        Settings.bot = self.session.query(Settings).filter(Settings.name == 'bot').first().value == 'true'
        Settings.make_joke = self.session.query(Settings).filter(Settings.name == 'make_joke').first().value == 'true'
        Settings.essay = self.session.query(Settings).filter(Settings.name == 'essay').first().value == 'true'
        Settings.random_post = self.session.query(Settings).filter(Settings.name == 'random_post').first().value == 'true'
        Settings.user_stats = self.session.query(Settings).filter(Settings.name == 'user_stats').first().value == 'true'
        Settings.call_admin = self.session.query(Settings).filter(Settings.name == 'call_admin').first().value == 'true'
        Settings.donate = self.session.query(Settings).filter(Settings.name == 'donate').first().value == 'true'

    def add(self, entity):
        if type(entity) is list:
            self.session.add_all(entity)
        else:
            self.session.add(entity)
        self.session.commit()
        return entity

    def update(self, entity, updated_value):
        try:
            entity.update(updated_value)
        except AttributeError:
            # setattr(entity, str([key for key in updated_value.keys()][0]).split('.')[1],
            #         str([key for key in updated_value.values()][0]))
            primary_key = inspect(type(entity)).primary_key[0].name
            self.session.query(type(entity)).filter(
                getattr(type(entity), primary_key) == getattr(entity, primary_key)).update(updated_value)
        finally:
            self.session.commit()
