from buttons import Buttons
from extensions import any_in, check_payload


class AnswerRules:
    __start_message = {
        'privilege': 'здравствуйте, хозяин',
        'main': 'приветствую тебя. я создан, чтобы передавать скрины админу, но я сам умею реферировать тексты и определять тему шутки. также вы можете поддержать паблик, если вам понравилось, что мы делаем'
    }

    __bad_words = [
        'ебал', 'гандон', 'пидор', 'хуй', 'соси', 'мразь', 'залупа', 'жопа', 'член', 'еблан', 'вагина', 'долбаеб', 'хуила'
    ]

    __main_menu_buttons = {
        'privilege': [
            [Buttons.screen_check, Buttons.admin_stats],
            [Buttons.jokes_check, Buttons.training],
            [Buttons.action_with_user, Buttons.bot_control]
        ],
        'main': [
            [Buttons.user_stats, Buttons.entertain],
            [Buttons.abstracting, Buttons.classification],
            [Buttons.donate_link]
        ]
    }

    rules = []

    def __init__(self):
        base_rules = [
            {
                'condition': lambda event: 'ты пидор' in event.text.lower(),
                'main': lambda vk, id: vk.send_message_sticker(id, 'а может ты пидор?', 49)
            },
            {
                'condition': lambda event: any_in(self.__bad_words, event.text.lower()) and event.attachments,
                'main': lambda vk, id: vk.send(id, 'ты неуважительно обратился ко мне, не буду смотреть твою пикчу')
            },
            {
                'condition': lambda event: any_in(self.__bad_words, event.text.lower()),
                'privilege': lambda vk, id: vk.send(id, 'хозяин, не нужно мне такие гадости писать, мне неприятно. лучше склепайте новых мемов'),
                'main': lambda vk, id: vk.send_message_sticker(id, f'я знаю что ты сидишь с id {id}, я тебя найду и уничтожу', 62)
            },
            {
                'condition': lambda event: event.attachments,
                'main': lambda vk, id: vk.send(id, 'проверяю твою фотокарточку, позже отпишу')
            },
            {
                'condition': lambda event: hasattr(event, 'payload'),
                'main': lambda vk, id: vk.send(id, 'данная функция находятся в разработке')
            },
        ]
        button_base_rules = [
            {
                'condition': lambda event: check_payload(event, 'start'),
                'privilege': lambda vk, id: vk.send(id, self.__start_message['privilege'], self.__main_menu_buttons['privilege']),
                'main': lambda vk, id: vk.send(id, self.__start_message['main'], self.__main_menu_buttons['main'])
            },
            {
                'condition': lambda event: 'кнопки' == event.text.lower() or check_payload(event, Buttons.to_main),
                'privilege': lambda vk, id: vk.send(id, 'as you wish', self.__main_menu_buttons['privilege']),
                'main': lambda vk, id: vk.send(id, 'as you wish', self.__main_menu_buttons['main'])
            },
            {
                'condition': lambda event: check_payload(event, Buttons.screen_check),
                'privilege': lambda vk, id: vk.send(id, 'здравствуйте, хозяин', [
                    [Buttons.ban_user, Buttons.unban_user],
                    [Buttons.abstracting, Buttons.to_main]
                ]),
            },
        ]

        self.rules = [
            *button_base_rules,
            *base_rules
        ]

    @staticmethod
    def default_action(vk, id):
        vk.send(id, 'что ты несешь-то вообще?')
