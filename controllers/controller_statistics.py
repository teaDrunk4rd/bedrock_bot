from buttons import Buttons
from controllers.controller import Controller
from db.models.joke import Joke
from db.models.settings import Settings
from db.models.user import User
from datetime import datetime, timedelta


class ControllerStatistics(Controller):
    def __init__(self):
        super().__init__()

        self.handlers = [
            {
                'condition': lambda vk, event, user: self.check_payload(event, Buttons.admin_stats),
                'admin': lambda vk, event, user: self.admin_stats(vk, event)
            },
            {
                'condition': lambda vk, event, user:
                    self.check_payload(event, Buttons.user_stats) and
                    self.check_access(Settings.user_stats, event.user_id),
                'main': lambda vk, event, user: self.user_stats(vk, event)
            },
        ]

    def admin_stats(self, vk, event):
        users_count = self.db.session.query(User).count()
        last_week_users_count = self.db.session.query(User)\
            .filter(User.last_interaction_date >= datetime.today() - timedelta(days=7)).count()

        not_viewed_jokes = self.db.session.query(Joke).filter(Joke.viewed != True).count()
        rated_jokes = self.db.session.query(Joke).filter(Joke.viewed == True, Joke.score > 0).count()
        shitty_jokes = self.db.session.query(Joke).filter(Joke.viewed == True, Joke.score == 0).count()

        vk.send(event.user_id, f'всего взаимодействовало с ботом: {users_count} '
                               f'{self.plural_form(users_count, "человек", "человека", "людей")}\n'
                               f'за последние 7 дней взаимодействовало с ботом: {last_week_users_count} '
                               f'{self.plural_form(last_week_users_count, "человек", "человека", "людей")}\n'
                               f'кол-во непроверенных приколов: {not_viewed_jokes}\n'
                               f'кол-во оценённых приколов: {rated_jokes}\n'
                               f'кол-во хуйовых приколов: {shitty_jokes}\n')

    def user_stats(self, vk, event):
        vk.send(event.user_id, self.get_user_stats(self.db, event.user_id))

    @staticmethod
    def get_user_stats(db, user_id):  # TODO: делать всё в одном запросе
        not_checked_jokes = db.session.query(Joke).filter(Joke.user_id == user_id, Joke.viewed != True).count()
        rated_jokes = db.session.query(Joke).filter(Joke.user_id == user_id, Joke.viewed == True, Joke.score > 0).count()
        shitty_jokes = db.session.query(Joke).filter(Joke.user_id == user_id, Joke.viewed == True, Joke.score == 0).count()

        return f'кол-во непроверенных приколов: {not_checked_jokes}\n' \
               f'кол-во оценённых приколов: {rated_jokes}\n' \
               f'кол-во хуйовых приколов: {shitty_jokes}\n'
