from buttons import Buttons
from controllers.controller import Controller
from db.db import db
from db.models.joke import Joke
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

    def admin_stats(self, vk, event):
        users_count = db.session.query(User).count()

        not_viewed_jokes = db.session.query(Joke).filter(Joke.viewed != True).count()
        rated_jokes = db.session.query(Joke).filter(Joke.viewed == True, Joke.score > 0).count()
        shitty_jokes = db.session.query(Joke).filter(Joke.viewed == True, Joke.score == 0).count()

        users = db.session.query(User).filter(User.role_id == Role.user).order_by(User.scores.desc()).all()[:10]
        user_names = vk.get_users_names(','.join([f'{user.user_id}' for user in users]))
        user_stats = '\n'.join([
            f'{num + 1}. {user_names[num]} (vk.com/id{user.user_id}): {user.scores}'
            for num, user in enumerate(users)
        ])

        vk.send(event.user_id, f'актив: {users_count} {self.plural_form(users_count, "человек", "человека", "людей")}\n'
                               f'кол-во непроверенных приколов: {not_viewed_jokes}\n'
                               f'кол-во оценённых приколов: {rated_jokes}\n'
                               f'кол-во хуйовых приколов: {shitty_jokes}\n' +
                ('\nтоп пользователей:\n' if user_stats != '' else '') +
                user_stats)

    @staticmethod
    def user_stats(vk, event):
        vk.send(event.user_id, ControllerStatistics.get_user_stats(event.user_id))

    @staticmethod
    def get_user_stats(user_id):  # TODO: делать всё в одном запросе
        not_checked_jokes = db.session.query(Joke).filter(Joke.user_id == user_id, Joke.viewed != True).count()
        rated_jokes = db.session.query(Joke).filter(Joke.user_id == user_id, Joke.viewed == True, Joke.score > 0).count()
        shitty_jokes = db.session.query(Joke).filter(Joke.user_id == user_id, Joke.viewed == True, Joke.score == 0).count()

        return f'кол-во непроверенных приколов: {not_checked_jokes}\n' \
               f'кол-во оценённых приколов: {rated_jokes}\n' \
               f'кол-во хуйовых приколов: {shitty_jokes}\n'
