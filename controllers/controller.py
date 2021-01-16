from ast import literal_eval
from buttons import Buttons
from config import Config
from db.db import db
from db.models.settings import Settings


class Controller:
    handlers = []

    start_message = {
        'admin': 'здравствуйте, хозяин',
        'main': 'привет, я — бот бедрока.\n'
                'вот что я могу:\n'
                '• передавать твои приколдесы админу.\n'
                '• реферировать текст: сокращать и сжимать его, выдавая основную суть в 3 предложениях.\n'
                '• отправлять любимые посты из бедрока.\n'
                '• оценивать твои фотографии. для этого нужно кинуть фотку в основном меню.\n'
                '• также через меня можно поддержать паблик.\n'
    }

    main_menu_buttons = {
        'admin': [
            [Buttons.jokes_check],
            [Buttons.action_with_user, Buttons.settings],
            [Buttons.admin_stats, Buttons.editors]
        ],
        'editor': [
            [Buttons.admin_stats],
            [Buttons.essay, Buttons.random_post]
        ],
        'main': [  # такой порядок должен быть у кнопок
            [Buttons.make_joke, Buttons.user_stats],  # убрать дублирование
            [Buttons.essay, Buttons.random_post],
            [Buttons.donate]
        ]
    }

    def update_user_buttons(self):
        buttons = [
            {'button': Buttons.make_joke, 'condition': Settings.make_joke},
            {'button': Buttons.user_stats, 'condition': Settings.user_stats},
            {'button': Buttons.essay, 'condition': Settings.essay},
            {'button': Buttons.random_post, 'condition': Settings.random_post},
            {'button': Buttons.donate, 'condition': Settings.donate},
        ]
        first_line, second_line, third_line = [], [], []
        for button in buttons:
            if button['condition']:
                if len(first_line) < 2:
                    first_line.append(button['button'])
                elif len(second_line) < 2:
                    second_line.append(button['button'])
                elif len(third_line) < 2:
                    third_line.append(button['button'])
        self.main_menu_buttons['main'] = [line for line in [first_line, second_line, third_line] if line != []]

    @staticmethod
    def check_access(setting, user_id):
        return setting or user_id in Config.admin_ids

    @staticmethod
    def check_payload(event, key):
        if type(key) is dict:  # is button
            key = Buttons.get_key(key)
        elif type(key) is list:
            keys = [Buttons.get_key(single_key) if type(key) is dict else single_key for single_key in key]
            return hasattr(event, 'payload') and literal_eval(event.payload).get('command') in keys

        return hasattr(event, 'payload') and literal_eval(event.payload).get('command') == key

    @staticmethod
    def any_in(values, message):
        return type(values) is list and any([val for val in values if val in message])

    @staticmethod
    def any_equal(values, message):
        return type(values) is list and any([val for val in values if val == message])

    @staticmethod
    def need_process_message(user_id):
        return db.get_user_path(user_id) not in [
            Buttons.get_key(Buttons.make_joke),
            Buttons.get_key(Buttons.essay)
        ]

    @staticmethod
    def plural_form(n, form1, form2, form5):
        n = abs(n) % 100
        n1 = n % 10
        if 10 < n < 20:
            return form5
        if 1 < n1 < 5:
            return form2
        if n1 == 1:
            return form1
        return form5
