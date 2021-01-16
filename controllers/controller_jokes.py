from buttons import Buttons
from controllers.controller import Controller
from db.models.joke import Joke
from db.models.settings import Settings
from db.models.user import User
from decorators.scores_getter import scores_getter


class ControllerJokes(Controller):
    def __init__(self):
        super().__init__()

        self.handlers = [
            {
                'condition': lambda vk, event, user: self.check_payload(event, Buttons.jokes_check),
                'admin': lambda vk, event, user: self.check_joke_first(vk, event, user)
            },
            {
                'condition': lambda vk, event, user: self.check_payload(event, Buttons.jokes_refresh),
                'admin': lambda vk, event, user: self.joke_refresh(vk, event, user)
            },
            {
                'condition': lambda vk, event, user: self.check_payload(event, Buttons.jokes_next),
                'admin': lambda vk, event, user: self.check_next_joke(vk, event, user)
            },
            {
                'condition': lambda vk, event, user: self.check_payload(event, Buttons.jokes_set_scores),
                'admin': lambda vk, event, user: self.set_scores_button(vk, event, user)
            },
            {
                'condition': lambda vk, event, user: user.compare_path(Buttons.jokes_set_scores),
                'admin': lambda vk, event, user: self.set_scores(vk, event, user)
            },

            {
                'condition': lambda vk, event, user:
                    self.check_payload(event, Buttons.make_joke) and
                    self.check_access(Settings.make_joke, event.user_id),
                'main': lambda vk, event, user: self.make_admin_laugh_button(vk, event, user)
            },
            {
                'condition': lambda vk, event, user: user.compare_path(Buttons.make_joke),
                'main': lambda vk, event, user: self.make_admin_laugh(vk, event, user)
            }
        ]

    def __get_jokes(self):
        return self.db.session.query(Joke).filter(Joke.viewed == False).order_by(Joke.id).all()

    def __over(self, vk, event, user):
        self.db.update(user, {User.path: ''})
        vk.send(event.user_id, [
            'шутки кончились',
            'шуток нет'
        ], self.main_menu_buttons['admin'])

    def check_joke(self, vk, event, user):
        jokes = self.__get_jokes()
        if any(jokes):
            joke = jokes[0]
            vk.send(
                event.user_id, '',
                [[Buttons.jokes_set_scores, Buttons.jokes_next], [Buttons.to_main]],
                joke.message_id
            )
        else:
            self.__over(vk, event, user)

    def check_joke_first(self, vk, event, user):
        jokes = self.__get_jokes()
        if any(jokes):
            vk.send(event.user_id, 'оцени прикол по 10-бальной шкале')
        self.check_joke(vk, event, user)

    def joke_refresh(self, vk, event, user):
        self.db.update(user, {User.path: ''})
        self.check_joke(vk, event, user)

    def check_next_joke(self, vk, event, user):
        jokes = self.__get_jokes()
        if any(jokes):
            joke = jokes[0]
            joke.viewed = True
            vk.send(
                joke.user_id,
                f'твою шутку оценили на 0 баллов\n',
                forward_messages=joke.message_id)
            self.db.session.commit()
            self.check_joke(vk, event, user)
        else:
            self.__over(vk, event, user)

    def set_scores_button(self, vk, event, user):
        self.db.update(user, {User.path: Buttons.get_key(Buttons.jokes_set_scores)})
        vk.send(event.user_id, 'сколько баллов поставишь шутнику?', [[Buttons.jokes_refresh]])

    @scores_getter
    def set_scores(self, vk, event, user, scores):
        jokes = self.__get_jokes()
        if any(jokes):
            joke = jokes[0]
            joke.viewed = True
            joke.score = scores
            message_prefix = 'поздравляю, ' if scores > 5 else ''
            vk.send(
                joke.user_id,
                f'{message_prefix}твою шутку оценили на {scores} {self.plural_form(scores, "балл", "балла", "баллов")}\n',
                forward_messages=joke.message_id
            )
            self.db.update(user, {User.path: ''})
            self.check_joke(vk, event, user)
        else:
            self.__over(vk, event, user)

    def make_admin_laugh_button(self, vk, event, user):
        self.db.update(user, {User.path: Buttons.get_key(Buttons.make_joke)})
        message = 'присылай шутку, передам её админу и он оценит'
        if any(user.jokes):
            message = [message, 'шути']
        vk.send(event.user_id, message, [[Buttons.to_main]])

    def make_admin_laugh(self, vk, event, user):
        self.db.add(Joke(event.user_id, event.message_id))
        self.db.update(user, {User.path: ''})
        vk.send(event.user_id, 'принято в обработку', self.main_menu_buttons['main'])
