from buttons import Buttons
from controllers.controller import Controller
from db.db import db
from db.models.joke import Joke
from db.models.settings import Settings
from db.models.user import User
from decorators.scores_getter import scores_getter


class ControllerJokes(Controller):
    def __init__(self):
        self.handlers = [
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.jokes_check),
                'admin': lambda vk, event: self.check_joke_first(vk, event)
            },
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.jokes_refresh),
                'admin': lambda vk, event: self.joke_refresh(vk, event)
            },
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.jokes_next),
                'admin': lambda vk, event: self.check_next_joke(vk, event)
            },
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.jokes_good),
                'admin': lambda vk, event: self.confirm_joke_button(vk, event)
            },
            {
                'condition': lambda vk, event: db.check_user_current_path(event.user_id, Buttons.jokes_good),
                'admin': lambda vk, event: self.confirm_joke(vk, event)
            },
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.jokes_cringe),
                'admin': lambda vk, event: self.reject_joke_button(vk, event)
            },
            {
                'condition': lambda vk, event: db.check_user_current_path(event.user_id, Buttons.jokes_cringe),
                'admin': lambda vk, event: self.reject_joke(vk, event)
            },

            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.make_joke) and
                                               self.check_access(Settings.make_joke, event.user_id),
                'main': lambda vk, event: self.make_admin_laugh_button(vk, event)
            },
            {
                'condition': lambda vk, event: db.check_user_current_path(event.user_id, Buttons.make_joke),
                'main': lambda vk, event: self.make_admin_laugh(vk, event)
            }
        ]

    def __get_jokes(self):
        return db.session.query(Joke).filter(Joke.viewed == False).order_by(Joke.id).all()

    def __over(self, vk, event):
        db.update(db.get_user(event.user_id), {User.path: ''})
        vk.send(event.user_id, [
            'шутки кончились',
            'шуток нет'
        ], self.main_menu_buttons['admin'])

    def check_joke(self, vk, event):
        jokes = self.__get_jokes()
        if any(jokes):
            joke = jokes[0]
            vk.send(
                event.user_id, '',
                [[Buttons.jokes_good, Buttons.jokes_cringe],
                 [Buttons.jokes_next, Buttons.to_main]], joke.message_id
            )
        else:
            self.__over(vk, event)

    def check_joke_first(self, vk, event):
        jokes = self.__get_jokes()
        if any(jokes):
            vk.send(event.user_id, 'ты можешь добавить или отнять баллы за шутку, учитывай, что 1 скрин — 1 балл')
        self.check_joke(vk, event)

    def joke_refresh(self, vk, event):
        user = db.get_user(event.user_id)
        db.update(user, {User.path: ''})
        self.check_joke(vk, event)

    def check_next_joke(self, vk, event):
        jokes = self.__get_jokes()
        if any(jokes):
            joke = jokes[0]
            joke.viewed = True
            db.session.commit()
            self.check_joke(vk, event)
        else:
            self.__over(vk, event)

    @staticmethod
    def confirm_joke_button(vk, event):
        user = db.get_user(event.user_id)
        db.update(user, {User.path: Buttons.get_key(Buttons.jokes_good)})
        vk.send(event.user_id, 'сколько очков добавить?', [[Buttons.jokes_refresh]])

    @staticmethod
    def reject_joke_button(vk, event):
        user = db.get_user(event.user_id)
        db.update(user, {User.path: Buttons.get_key(Buttons.jokes_cringe)})
        vk.send(event.user_id, 'сколько очков отнять?', [[Buttons.jokes_refresh]])

    @scores_getter
    def confirm_joke(self, vk, event, scores):
        jokes = self.__get_jokes()
        if any(jokes):
            joke = jokes[0]
            joke.viewed = True
            joke.score = scores
            db.update(db.get_user(joke.user_id), {User.scores: User.scores + scores})
            vk.send(joke.user_id,
                    f'поздравляю, твою шутку оценили на {scores} {self.plural_form(scores, "очко", "очка", "очков")}\n'
                    f'на данный момент у тебя {joke.user.scores} {self.plural_form(joke.user.scores, "очко", "очка", "очков")}',
                    forward_messages=joke.message_id)
            self.check_joke(vk, event)
        else:
            self.__over(vk, event)

    @scores_getter
    def reject_joke(self, vk, event, scores):
        jokes = self.__get_jokes()
        if any(jokes):
            joke = jokes[0]
            joke.viewed = True
            joke.score = scores * -1
            db.update(db.get_user(joke.user_id), {User.scores: User.scores - scores})
            scores_str = f'-{scores}' if scores != 0 else scores
            vk.send(joke.user_id,
                    f'твою шутку оценили на {scores_str} {self.plural_form(scores, "очко", "очка", "очков")}\n'
                    f'на данный момент у тебя {joke.user.scores} {self.plural_form(joke.user.scores, "очко", "очка", "очков")}',
                    forward_messages=joke.message_id)
            self.check_joke(vk, event)
        else:
            self.__over(vk, event)

    @staticmethod
    def make_admin_laugh_button(vk, event):
        user = db.get_user(event.user_id)
        db.update(user, {User.path: Buttons.get_key(Buttons.make_joke)})
        message = 'присылай шутку, админ оценит и добавит баллы, но если скинешь кринж — то баллы отнимут.' \
                  ' юмор — несомненно субъективен, но ты можешь рискнуть'
        if any(user.first().jokes):
            message = [message, 'шути']
        vk.send(event.user_id, message, [[Buttons.to_main]])

    def make_admin_laugh(self, vk, event):
        db.add(Joke(event.user_id, event.message_id))
        user = db.get_user(event.user_id)
        db.update(user, {User.path: ''})
        vk.send(event.user_id, 'принято в обработку', self.main_menu_buttons['main'])
