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

    __raw_main_buttons = [  # такой порядок должен быть у кнопок
        [Buttons.make_joke, Buttons.user_stats],
        [Buttons.essay, Buttons.random_post],
        [Buttons.call_admin, Buttons.donate]
    ]

    main_menu_buttons = {
        'admin': [
            [Buttons.jokes_check, Buttons.admin_stats],
            [Buttons.action_with_user, Buttons.settings],
        ],
        'main': []
    }

    settings_buttons = [
        {
            'block': Buttons.block_bot,
            'unblock': Buttons.unblock_bot,
            'setting': 'bot'
        },
        {
            'user_button': Buttons.make_joke,
            'block': Buttons.block_make_joke,
            'unblock': Buttons.unblock_make_joke,
            'setting': 'make_joke'
        },
        {
            'user_button': Buttons.user_stats,
            'block': Buttons.block_stats,
            'unblock': Buttons.unblock_stats,
            'setting': 'user_stats'
        },
        {
            'user_button': Buttons.essay,
            'block': Buttons.block_essay,
            'unblock': Buttons.unblock_essay,
            'setting': 'essay'
        },
        {
            'user_button': Buttons.random_post,
            'block': Buttons.block_random_post,
            'unblock': Buttons.unblock_random_post,
            'setting': 'random_post'
        },
        {
            'user_button': Buttons.call_admin,
            'block': Buttons.block_call_admin,
            'unblock': Buttons.unblock_call_admin,
            'setting': 'call_admin'
        },
        {
            'user_button': Buttons.donate,
            'block': Buttons.block_donate,
            'unblock': Buttons.unblock_donate,
            'setting': 'donate'
        }
    ]

    def update_user_buttons(self):
        first_line, second_line, third_line = [], [], []
        for button in self.settings_buttons:
            if button.get('user_button') and Settings.get(button['setting']):
                if len(first_line) < 2:
                    first_line.append(button['user_button'])
                elif len(second_line) < 2:
                    second_line.append(button['user_button'])
                elif len(third_line) < 2:
                    third_line.append(button['user_button'])
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
