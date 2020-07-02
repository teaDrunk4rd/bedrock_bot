
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
        'main': lambda vk, id: vk.send(id, 'ты неуважительно обратился ко мне, не буду смотреть твою пикчу')
    },
    {
        'condition': lambda event: any_in(words['bad'], event.text.lower()),
        'privilege': lambda vk, id: vk.send(id, 'хозяин, не нужно мне такие гадости писать, мне неприятно. лучше склепайте новых мемов'),
        'main': lambda vk, id: vk.send_message_sticker(id, f'я знаю что ты сидишь с id {id}, я тебя найду и уничтожу', 62)
    },
    {
        'condition': lambda event: event.attachments,
        'main': lambda vk, id: vk.send(id, 'проверяю твою фотокарточку, позже отпишу')
    },
    {
        'condition': lambda event: any_in(words['hello'], event.text.lower()),
        'privilege': lambda vk, id: vk.send(id, 'здравствуйте, хозяин'),
        'main': lambda vk, id: vk.send(id, f'и тебя приветствую')
    },
    {
        'condition': lambda event: 'кнопки' in event.text.lower(),
        'privilege': lambda vk, id: vk.send(id, 'держи', [
            [('Проверить скрин', 'primary'), ('Статистика', 'primary')],
            [('Забанить', 'negative'), ('Разбанить', 'positive')]
        ]),
        'main': lambda vk, id: vk.send(id, 'держи', [
            [('Статистика', 'primary'), ('Реферат', 'primary')],
            [('Поддержать', 'positive')]
        ])
    },
    {
        'condition': lambda event: any_in(
            ['проверить скрин', 'статистика', 'забанить', 'разбанить', 'статистика', 'реферат', 'поддержать'],
            event.text.lower()),
        'main': lambda vk, id: vk.send(id, 'данная функция находятся в разработке')
    },
]


def any_in(values, message):
    return any([val for val in values if val in message])
