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
    screen_refresh = get_text_button('Назад', 'secondary', get_command('screen_refresh'))
    screen_confirm = get_text_button('Подтвердить', 'positive', get_command('screen_confirm'))
    screen_reject = get_text_button('Отклонить', 'negative', get_command('screen_reject'))
    comment_screen_reject = get_text_button('Отклонить с комментом', 'negative', get_command('comment_screen_reject'))

    jokes_check = get_text_button('Проверка приколов', 'primary', get_command('jokes_check'))
    jokes_refresh = get_text_button('Назад', 'secondary', get_command('jokes_refresh'))
    jokes_good = get_text_button('Godnota', 'positive', get_command('jokes_good'))
    jokes_cringe = get_text_button('Cringe', 'negative', get_command('jokes_cringe'))
    jokes_next = get_text_button('Следующая', 'secondary', get_command('jokes_next'))

    action_with_user = get_text_button('Действия с пользователем', 'primary', get_command('action_with_user'))
    unban_user = get_text_button('Разбанить', 'positive', get_command('unban_user'))
    ban_user = get_text_button('Забанить', 'negative', get_command('ban_user'))
    add_scores = get_text_button('Добавить очки', 'positive', get_command('add_scores'))
    remove_scores = get_text_button('Отнять очки', 'negative', get_command('remove_scores'))

    admin_stats = get_text_button('Статистика', 'secondary', get_command('admin_stats'))

    editors = get_text_button('Редакторы', 'secondary', get_command('editors'))
    add_editor = get_text_button('Добавить', 'positive', get_command('add_editor'))
    remove_editor = get_text_button('Убрать', 'negative', get_command('remove_editor'))

    settings = get_text_button('Управление ботом', 'primary', get_command('settings'))
    block_bot = get_text_button('Остановить бота', 'negative', get_command('block', 'bot'))
    unblock_bot = get_text_button('Запустить бота', 'positive', get_command('unblock', 'bot'))
    block_screen = get_text_button('Остановить скрины', 'negative', get_command('block', 'screen'))
    unblock_screen = get_text_button('Запустить скрины', 'positive', get_command('unblock', 'screen'))
    block_make_joke = get_text_button('Остановить "Насмеши админа"', 'negative', get_command('block', 'make_joke'))
    unblock_make_joke = get_text_button('Запустить "Насмеши админа"', 'positive', get_command('unblock', 'make_joke'))
    block_essay = get_text_button('Остановить рефераты', 'negative', get_command('block', 'essay'))
    unblock_essay = get_text_button('Запустить рефераты', 'positive', get_command('unblock', 'essay'))
    block_random_post = get_text_button('Остановить случайный пост', 'negative', get_command('block', 'random_post'))
    unblock_random_post = get_text_button('Запустить случайный пост', 'positive', get_command('unblock', 'random_post'))
    block_stats = get_text_button('Остановить статистику', 'negative', get_command('block', 'user_stats'))
    unblock_stats = get_text_button('Запустить статистику', 'positive', get_command('unblock', 'user_stats'))
    block_donate = get_text_button('Остановить донаты', 'negative', get_command('block', 'donate'))
    unblock_donate = get_text_button('Запустить донаты', 'positive', get_command('unblock', 'donate'))

    send_screen = get_text_button('Кинуть скрин', 'positive', get_command('send_screen'))

    make_joke = get_text_button('Насмешить админа', 'positive', get_command('make_joke'))

    user_stats = get_text_button('Статистика', 'primary', get_command('user_stats'))

    essay = get_text_button('Реферат', 'primary', get_command('essay'))

    random_post = get_text_button('Случайный пост', 'secondary', get_command('random_post'))

    donate = get_app_button('Поддержать', Config.donate_app_id, f'-{Config.group_id}')

    @staticmethod
    def get_key(button):
        return button['action']['payload']['command']

    @staticmethod
    def get_args(button):
        return button['action']['payload'].get('args')

    @staticmethod
    def change_command(main_button, action_button):
        new_button = copy.deepcopy(main_button)
        new_button['action']['payload'] = action_button['action']['payload']
        return new_button

    @staticmethod
    def get_label(button):
        return button['action']['label'].lower()


button_labels = [
    Buttons.get_label(getattr(Buttons, a))
    for a in dir(Buttons) if not a.startswith('__') and not callable(getattr(Buttons, a))
]
