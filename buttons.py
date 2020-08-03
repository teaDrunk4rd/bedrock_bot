from config import Config
import copy


def get_text_button(label, color, payload=None):
    return {
        'action': {
            'type': 'text',
            'payload': payload,
            'label': label
        },
        'color': color
    }


def get_app_button(label, app_id, group_id):
    return {
        'action': {
            'type': 'open_app',
            'app_id': app_id,
            'owner_id': group_id,
            'label': label
        }
    }


def get_link_button(label, link):
    return {
        'action': {
            'type': 'open_link',
            'link': link,
            'label': label
        }
    }


def get_command(key, args=None):
    vk_command = {
        'command': key
    }
    if args:
        vk_command.update({'args': args})
    return vk_command


class Buttons:
    to_main = get_text_button('Назад', 'secondary', get_command('to_main'))

    screen_check = get_text_button('Проверка скринов', 'primary', get_command('screen_check'))
    screen_confirm = get_text_button('Подтвердить', 'positive', get_command('screen_confirm'))
    screen_reject = get_text_button('Отклонить', 'negative', get_command('screen_reject'))

    admin_stats = get_text_button('Статистика', 'primary', get_command('admin_stats'))

    jokes_check = get_text_button('Проверка приколов', 'primary', get_command('jokes_check'))
    jokes_refresh = get_text_button('Назад', 'secondary', get_command('jokes_refresh'))
    jokes_good = get_text_button('Godnota', 'positive', get_command('jokes_good'))
    jokes_cringe = get_text_button('Cringe', 'negative', get_command('jokes_cringe'))
    jokes_next = get_text_button('Следующая', 'secondary', get_command('jokes_next'))

    training = get_text_button('Обучение шуткам', 'primary', get_command('training'))  # TODO: брать из БД классы и строить кнопки при старте бота и при добавлении класса

    action_with_user = get_text_button('Действия с пользователем', 'primary', get_command('action_with_user'))
    unban_user = get_text_button('Разбанить', 'positive', get_command('unban_user'))  # TODO: среди бана/разбана должна показываться только 1 кнопка
    ban_user = get_text_button('Забанить', 'negative', get_command('ban_user'))
    add_scores = get_text_button('Добавить очки', 'positive', get_command('add_scores'))
    remove_scores = get_text_button('Отнять очки', 'negative', get_command('remove_scores'))

    bot_control = get_text_button('Управление ботом', 'primary', get_command('bot_control'))
    start_bot = get_text_button('Запустить', 'positive', get_command('start_bot'))  # TODO: среди запустить/приостановить должна показываться только 1 кнопка
    pause_bot = get_text_button('Приостановить', 'negative', get_command('pause_bot'))
    block_screen = get_text_button('Запустить скрины', 'positive', get_command('screen_block'))
    unblock_screen = get_text_button('Приостановить скрины', 'negative', get_command('screen_unblock'))
    block_donate = get_text_button('Запустить донаты', 'positive', get_command('donate_block'))
    unblock_donate = get_text_button('Приостановить донаты', 'negative', get_command('donate_unblock'))
    block_stats = get_text_button('Запустить статистику', 'positive', get_command('stats_block'))
    unblock_stats = get_text_button('Приостановить статистику', 'negative', get_command('stats_unblock'))
    block_essay = get_text_button('Запустить рефераты', 'positive', get_command('essay_block'))
    unblock_essay = get_text_button('Приостановить рефераты', 'negative', get_command('essay_unblock'))
    block_classification = get_text_button('Запустить классификацию', 'positive', get_command('classification_block'))
    unblock_classification = get_text_button('Приостановить классификацию', 'negative', get_command('classification_unblock'))
    block_entertain = get_text_button('Запустить "Насмеши админа"', 'positive', get_command('entertain_block'))
    unblock_entertain = get_text_button('Приостановить "Насмеши админа"', 'negative', get_command('entertain_unblock'))

    send_screen = get_text_button('Кинуть скрин', 'positive', get_command('send_screen'))

    user_stats = get_text_button('Статистика', 'secondary', get_command('user_stats'))

    entertain = get_text_button('Насмешить админа', 'positive', get_command('entertain'))

    essay = get_text_button('Реферат', 'primary', get_command('essay'))

    classification = get_text_button('Определить тему шутки', 'primary', get_command('classification'))

    donate = get_app_button('Поддержать', Config.donate_app_id, f'-{Config.group_id}')

    @staticmethod
    def get_key(button):
        return button['action']['payload']['command']

    @staticmethod
    def change_command(main_button, action_button):
        new_button = copy.deepcopy(main_button)
        new_button['action']['payload'] = action_button['action']['payload']
        return new_button

    @staticmethod
    def get_label(button):
        return button['action']['label'].lower()


user_button_labels = [
    Buttons.get_label(button) for button in
    [
        Buttons.to_main, Buttons.send_screen, Buttons.user_stats, Buttons.entertain, Buttons.essay,
        Buttons.classification, Buttons.donate
    ]
]
admin_button_labels = [
    Buttons.get_label(getattr(Buttons, a))
    for a in dir(Buttons) if not a.startswith('__') and not callable(getattr(Buttons, a))
]
