from ast import literal_eval
from buttons import Buttons


class Controller:  # TODO: декоратор для отправки сообщений?
    handlers = []

    start_message = {
        'privilege': 'здравствуйте, хозяин',
        'main': 'приветствую тебя. я создан, чтобы передавать скрины админу, но я сам умею реферировать тексты '
                'и определять тему шутки. также вы можете поддержать паблик, если вам понравилось, что мы делаем',
    }

    bad_words = [
        'ебал', 'гандон', 'пидор', 'хуй', 'соси', 'мразь', 'залупа',
        'жопа', 'член', 'еблан', 'вагина', 'долбаеб', 'хуила', 'пизда'
    ]

    main_menu_buttons = {
        'privilege': [
            [Buttons.screen_check, Buttons.admin_stats],
            [Buttons.jokes_check, Buttons.training],
            [Buttons.action_with_user, Buttons.bot_control]
        ],
        'main': [
            [Buttons.send_screen, Buttons.entertain],
            [Buttons.essay, Buttons.classification],
            [Buttons.user_stats, Buttons.donate]
        ]
    }

    action_with_users_buttons = [
        [Buttons.ban_user, Buttons.unban_user],
        [Buttons.add_scores, Buttons.remove_scores],
        [Buttons.to_main]
    ]

    @staticmethod
    def check_payload(event, key):
        if type(key) is dict:  # is button
            key = Buttons.get_key(key)
        return hasattr(event, 'payload') and literal_eval(event.payload).get('command') == key

    @staticmethod
    def any_in(values, message):
        return type(values) is list and any([val for val in values if val in message])
