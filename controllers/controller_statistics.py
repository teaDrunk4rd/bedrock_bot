from buttons import Buttons
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
        users = db.session.query(User).filter(User.role_id == Role.user).order_by(User.scores.desc()).all()[:10]
        user_names = vk.get_users_names(','.join([f'{user.user_id}' for user in users]))
        user_stats = '\n'.join([
            f'{num + 1}. {user_names[num]} (vk.com/id{user.user_id}): {user.scores}'
            for num, user in enumerate(users)
        ])
        vk.send(event.user_id, f'кол-во непроверенных скринов: {not_checked_screens}\n'
                               f'кол-во принятых скринов: {confirmed_screens}\n'
                               f'кол-во отклоненных скринов: {rejected_screens}\n'
                               f'кол-во непросмотренных приколов: {not_viewed_jokes}\n' +
                ('\nтоп пользователей:\n' if user_stats != '' else '') +
                user_stats)

    @staticmethod
    def user_stats(vk, event):
        vk.send(event.user_id, ControllerStatistics.get_user_stats(event.user_id))

    @staticmethod
    def get_user_stats(user_id):
        scores = db.session.query(User).filter(User.user_id == user_id).first().scores
        place_in_top = db.session.execute(f'''
            with users as (     
                select *, row_number() over(order by users.scores desc) as num 
                from users     
                where role_id = {Role.user}
            ), num as (     
                select num     
                from users     
                where user_id = {user_id} 
            ) 
            select num.num, count(users) 
            from num join users on true 
            group by num.num''').first()
        place_in_top_message = f'место в топе: {place_in_top[0]} из {place_in_top[1]}\n' if place_in_top else ''
        not_checked_screens = db.session.query(Picture).filter(Picture.user_id == user_id, Picture.status_id == PictureStatus.not_checked).count()
        confirmed_screens = db.session.query(Picture).filter(Picture.user_id == user_id, Picture.status_id == PictureStatus.confirmed).count()
        rejected_screens = db.session.query(Picture).filter(Picture.user_id == user_id, Picture.status_id == PictureStatus.rejected).count()
        scores_jokes = db.session.query(Joke).filter(Joke.user_id == user_id, Joke.score > 0).count()
        return f'{place_in_top_message}\n' \
               f'кол-во очков: {scores}\n' \
               f'кол-во непроверенных скринов: {not_checked_screens}\n' \
               f'кол-во принятых скринов: {confirmed_screens}\n' \
               f'кол-во отклоненных скринов: {rejected_screens}\n' \
               f'кол-во засчитанных приколов: {scores_jokes}\n'
