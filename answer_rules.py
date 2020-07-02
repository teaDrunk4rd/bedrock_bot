
def default_action(vk, id):
    vk.send(id, 'что ты несешь-то вообще?')

words = {
    'hello': ['привет', 'здравствуй', 'здаров', 'салам'],
    'bad': ['ебал', 'гандон', 'пидор', 'хуй', 'соси', 'мразь', 'залупа', 'жопа', 'член', 'еблан', 'вагина', 'долбаеб', 'хуила']
}

answer_rules = [
    {
        'condition': lambda event: 'ты пидор' in event.text.lower(),
        'main': lambda vk, id: vk.send_message_sticker(id, 'а может ты пидор?', 49)
    },
    {
        'condition': lambda event: any_in(words['bad'], event.text.lower()) and event.attachments,
        'main': lambda vk, id: vk.send(id, 'не буду смотреть твоё дерьмо')
    },
    {
        'condition': lambda event: any_in(words['bad'], event.text.lower()),
        'privilege': lambda vk, id: vk.send(id, 'хозяин, не нужно мне такие гадости писать, мне неприятно. лучше склепайте новых мемов'),
        'main': lambda vk, id: vk.send_message_sticker(id, f'я знаю что ты сидишь с id {id}, я тебя найду и уничтожу', 62)
    },
    {
        'condition': lambda event: event.attachments,
        'main': lambda vk, id: vk.send(id, 'Ох, дедушка не ожидал столько писем с фотокарточками. Подожди несколько минут, я обязательно вернусь')
    },
    {
        'condition': lambda event: any_in(words['hello'], event.text.lower()),
        'privilege': lambda vk, id: vk.send(id, 'здравствуйте, хозяин'),
        'main': lambda vk, id: vk.send(id, f'и тебя приветствую')
    },
]


def any_in(values, message):
    return any([val for val in values if val in message])
