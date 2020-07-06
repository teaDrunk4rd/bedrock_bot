
def get_button(label, color, payload=''):
    return {
        'action': {
            'type': 'text',
            'payload': payload,
            'label': label
        },
        'color': color
    }


def command(key, args=None):
    vk_command = {
        'command': key
    }
    if args:
        vk_command.update({'args': args})
    return vk_command


class Buttons:  # TODO: предусмотреть отсутствие кнопок у админа при запуске бота и обновление кнопок
    to_main = get_button('Назад', 'secondary', command('to_main'))

    screen_check = get_button('Проверка скрина', 'primary', command('screen_check'))
    screen_confirm = get_button('Подтвердить', 'positive', command('screen_confirm'))
    screen_reject = get_button('Отвергнуть', 'negative', command('screen_reject'))

    admin_stats = get_button('Статистика', 'primary', command('admin_stats'))

    action_with_user = get_button('Действия с пользователем', 'primary', command('action_with_user'))
    unban_user = get_button('Разбанить', 'positive', command('unban_user'))  # TODO: среди бана/разбана должна показываться только 1 кнопка
    ban_user = get_button('Забанить', 'negative', command('ban_user'))
    add_scores = get_button('Добавить очки', 'positive', command('add_scores'))
    remove_scores = get_button('Отнять очки', 'negative', command('remove_scores'))

    bot_control = get_button('Управление ботом', 'primary', command('bot_control'))
    start_bot = get_button('Запустить', 'positive', command('start_bot'))  # TODO: среди запустить/приостановить должна показываться только 1 кнопка
    pause_bot = get_button('Приостановить', 'negative', command('pause_bot'))  # TODO: в payload передать json {bot:start}, чтобы была 1 ф-я обработки
    screen_block = get_button('Запустить скрины', 'positive', command('screen_block'))
    screen_unblock = get_button('Приостановить скрины', 'negative', command('screen_unblock'))
    donate_block = get_button('Запустить донаты', 'positive', command('donate_block'))
    donate_unblock = get_button('Приостановить донаты', 'negative', command('donate_unblock'))
    stats_block = get_button('Запустить статистику', 'positive', command('stats_block'))
    stats_unblock = get_button('Приостановить статистику', 'negative', command('stats_unblock'))
    abstracting_block = get_button('Запустить рефераты', 'positive', command('abstracting_block'))
    abstracting_unblock = get_button('Приостановить рефераты', 'negative', command('abstracting_unblock'))
    classification_block = get_button('Запустить классификацию', 'positive', command('classification_block'))
    classification_unblock = get_button('Приостановить классификацию', 'negative', command('classification_unblock'))
    entertain_block = get_button('Запустить "Насмеши админа"', 'positive', command('entertain_block'))
    entertain_unblock = get_button('Приостановить "Насмеши админа"', 'negative', command('entertain_unblock'))

    training = get_button('Обучение шуткам', 'primary', command('training'))  # TODO: брать из БД классы и строить кнопки при старте бота и при добавлении класса

    jokes_check = get_button('Проверка приколов', 'primary', command('jokes_check'))
    jokes_good = get_button('Godnota', 'positive', command('jokes_good'))
    jokes_cringe = get_button('Cringe', 'negative', command('jokes_cringe'))
    jokes_next = get_button('Следующая', 'secondary', command('jokes_next'))

    user_stats = get_button('Статистика', 'primary', command('user_stats'))

    abstracting = get_button('Реферат', 'primary', command('abstracting'))

    classification = get_button('Определить тему шутки', 'primary', command('classification'))

    entertain = get_button('Насмешить админа', 'positive', command('classification'))

    donate_link = get_button('Поддержать', 'positive', command('donate_link'))

    @staticmethod
    def get_key(button):
        return button['action']['payload']['command']
