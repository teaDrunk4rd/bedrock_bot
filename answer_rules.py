from ast import literal_eval
# TODO: сделать класс Answer_rules
from buttons import Buttons


def default_action(vk, id):
    vk.send(id, 'что ты несешь-то вообще?')


bad_words = ['ебал', 'гандон', 'пидор', 'хуй', 'соси', 'мразь', 'залупа', 'жопа', 'член', 'еблан', 'вагина', 'долбаеб', 'хуила']

answer_rules = [
    {
        'condition': lambda event: 'привет' == event.text.lower() or check_payload(event, 'start'),  # payload is start or buttons (for start write rules for users)
        'privilege': lambda vk, id: vk.send(id, 'здравствуйте, хозяин', [
            [Buttons.screen_check, Buttons.admin_stats],
            [Buttons.action_with_user, Buttons.bot_control]
        ]),
        'main': lambda vk, id: vk.send(id, 'приветствую тебя', [  # я создан, чтобы передавать скрины админу. я умею реферировать тексты, определять тему шутки. также вы можете поддержать паблик, если вам понравилось, что мы делаем
            [Buttons.user_stats, Buttons.abstracting],
            [Buttons.donate_link]
        ])
    },
    # {
    #     'condition': lambda event: 'привет' == event.text.lower() or check_payload(event, Buttons.get_key(Buttons.screen_check)),
    #     'privilege': lambda vk, id: vk.send(id, 'здравствуйте, хозяин', [
    #         [Buttons.ban_user, Buttons.unban_user],
    #         [Buttons.abstracting, Buttons.abstracting_block]
    #     ]),
    # },
    {
        'condition': lambda event: 'ты пидор' in event.text.lower(),
        'main': lambda vk, id: vk.send_message_sticker(id, 'а может ты пидор?', 49)
    },
    {
        'condition': lambda event: any_in(bad_words, event.text.lower()) and event.attachments,
        'main': lambda vk, id: vk.send(id, 'ты неуважительно обратился ко мне, не буду смотреть твою пикчу')
    },
    {
        'condition': lambda event: any_in(bad_words, event.text.lower()),
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


def any_in(values, message):
    return type(values) is list and any([val for val in values if val in message])


def check_payload(event, command):
    return hasattr(event, 'payload') and literal_eval(event.payload).get('command') == command
