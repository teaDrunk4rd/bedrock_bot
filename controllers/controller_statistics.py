from buttons import Buttons
from config import Config
from controllers.controller import Controller
from db.db import db
from db.models.joke import Joke
from db.models.picture import Picture
from db.models.picture_status import PictureStatus
from db.models.role import Role
from db.models.settings import Settings
from db.models.user import User


class ControllerStatistics(Controller):
    def __init__(self):
        self.handlers = [
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.admin_stats),
                'admin': lambda vk, event: self.admin_stats(vk, event),
                'editor': lambda vk, event: self.admin_stats(vk, event)
            },
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.user_stats) and
                                               self.check_access(Settings.user_stats, event.user_id),
                'main': lambda vk, event: self.user_stats(vk, event)
            },
        ]

    @staticmethod
    def admin_stats(vk, event):
        not_checked_screens = db.session.query(Picture).filter(Picture.status_id == PictureStatus.not_checked).count()
        confirmed_screens = db.session.query(Picture).filter(Picture.status_id == PictureStatus.confirmed).count()
        rejected_screens = db.session.query(Picture).filter(Picture.status_id == PictureStatus.rejected).count()
        not_viewed_jokes = db.session.query(Joke).filter(Joke.viewed != True).count()
        users = db.session.query(User).filter(User.user_id == Role.user).order_by(User.scores).all()[:10]  # .filter(User.user_id.notin_(Config.admin_ids))
        user_stats = ''.join([
            f'{num + 1}. {vk.get_user_name(user.user_id)}(vk.com/id{user.user_id}): {user.scores}\n'
            for num, user in enumerate(users)
        ])
        vk.send(event.user_id, f'кол-во непроверенных скринов: {not_checked_screens}\n'
                               f'кол-во принятых скринов: {confirmed_screens}\n'
                               f'кол-во отклоненных скринов: {rejected_screens}\n'
                               f'кол-во непросмотренных приколов: {not_viewed_jokes}\n' +
                user_stats)

    @staticmethod
    def user_stats(vk, event):
        vk.send(event.user_id, ControllerStatistics.get_user_stats(event.user_id))

    @staticmethod
    def get_user_stats(user_id):
        scores = db.session.query(User).filter(User.user_id == user_id).first().scores
        not_checked_screens = db.session.query(Picture).filter(Picture.user_id == user_id, Picture.status_id == PictureStatus.not_checked).count()
        confirmed_screens = db.session.query(Picture).filter(Picture.user_id == user_id, Picture.status_id == PictureStatus.confirmed).count()
        rejected_screens = db.session.query(Picture).filter(Picture.user_id == user_id, Picture.status_id == PictureStatus.rejected).count()
        scores_jokes = db.session.query(Joke).filter(Joke.user_id == user_id, Joke.score > 0).count()
        return f'кол-во очков: {scores}\n' \
               f'кол-во непроверенных скринов: {not_checked_screens}\n' \
               f'кол-во принятых скринов: {confirmed_screens}\n' \
               f'кол-во отклоненных скринов: {rejected_screens}\n' \
               f'кол-во засчитанных приколов: {scores_jokes}\n'
