from extensions import get_button, get_command


class Buttons:  # TODO: предусмотреть отсутствие кнопок у админа при запуске бота и обновление кнопок
    to_main = get_button('Назад', 'secondary', get_command('to_main'))

    screen_check = get_button('Проверка скрина', 'primary', get_command('screen_check'))
    screen_confirm = get_button('Подтвердить', 'positive', get_command('screen_confirm'))
    screen_reject = get_button('Отвергнуть', 'negative', get_command('screen_reject'))

    admin_stats = get_button('Статистика', 'primary', get_command('admin_stats'))
    unban_user = get_button('Разбанить', 'positive', get_command('unban_user'))  # TODO: среди бана/разбана должна показываться только 1 кнопка
    ban_user = get_button('Забанить', 'negative', get_command('ban_user'))
    add_scores = get_button('Добавить очки', 'positive', get_command('add_scores'))
    remove_scores = get_button('Отнять очки', 'negative', get_command('remove_scores'))

    jokes_check = get_button('Проверка приколов', 'primary', get_command('jokes_check'))
    jokes_good = get_button('Godnota', 'positive', get_command('jokes_good'))
    jokes_cringe = get_button('Cringe', 'negative', get_command('jokes_cringe'))
    jokes_next = get_button('Следующая', 'secondary', get_command('jokes_next'))

    training = get_button('Обучение шуткам', 'primary', get_command('training'))  # TODO: брать из БД классы и строить кнопки при старте бота и при добавлении класса

    action_with_user = get_button('Действия с пользователем', 'primary', get_command('action_with_user'))

    bot_control = get_button('Управление ботом', 'primary', get_command('bot_control'))
    start_bot = get_button('Запустить', 'positive', get_command('start_bot'))  # TODO: среди запустить/приостановить должна показываться только 1 кнопка
    pause_bot = get_button('Приостановить', 'negative', get_command('pause_bot'))  # TODO: в payload передать json {bot:start}, чтобы была 1 ф-я обработки
    screen_block = get_button('Запустить скрины', 'positive', get_command('screen_block'))
    screen_unblock = get_button('Приостановить скрины', 'negative', get_command('screen_unblock'))
    donate_block = get_button('Запустить донаты', 'positive', get_command('donate_block'))
    donate_unblock = get_button('Приостановить донаты', 'negative', get_command('donate_unblock'))
    stats_block = get_button('Запустить статистику', 'positive', get_command('stats_block'))
    stats_unblock = get_button('Приостановить статистику', 'negative', get_command('stats_unblock'))
    abstracting_block = get_button('Запустить рефераты', 'positive', get_command('abstracting_block'))
    abstracting_unblock = get_button('Приостановить рефераты', 'negative', get_command('abstracting_unblock'))
    classification_block = get_button('Запустить классификацию', 'positive', get_command('classification_block'))
    classification_unblock = get_button('Приостановить классификацию', 'negative', get_command('classification_unblock'))
    entertain_block = get_button('Запустить "Насмеши админа"', 'positive', get_command('entertain_block'))
    entertain_unblock = get_button('Приостановить "Насмеши админа"', 'negative', get_command('entertain_unblock'))

    user_stats = get_button('Статистика', 'positive', get_command('user_stats'))

    entertain = get_button('Насмешить админа', 'positive', get_command('classification'))

    abstracting = get_button('Реферат', 'primary', get_command('abstracting'))

    classification = get_button('Определить тему шутки', 'primary', get_command('classification'))

    donate_link = get_button('Поддержать', 'secondary', get_command('donate_link'))

    @staticmethod
    def get_key(button):
        return button['action']['payload']['command']
