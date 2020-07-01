import vk_api
from vk_api.longpoll import VkEventType
from config import Config
from vk_methods import Vk

admin_ids = [132228887, 322270793]
abuses = ['ебал', 'гандон', 'пидор', 'хуй', 'соси', 'мразь', 'залупа', 'жопа', 'член', 'еблан', 'вагина', 'долбаеб']
answer_rules = {
    'ты пидор': lambda id: vk.send_message_sticker(id, 'а может ты пидор?', 49)
}

vk = Vk(vk_api.VkApi(token=Config.token))

for event in vk.longpool.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        message = event.text.lower()
        if any([rule for rule in answer_rules if rule in message]):
            answer_rules[[rule for rule in answer_rules if rule in message][0]](event.user_id)
        elif any([abuse for abuse in abuses if abuse in message]):
            if event.user_id in admin_ids:
                vk.send_message_sticker(event.user_id, 'хозяин, не нужно мне такие гадости писать, мне неприятно. лучше склепайте новых мемов')
            else:
                vk.send_message_sticker(event.user_id, f'мразь, я знаю что ты сидишь с id {event.user_id}, я тебя найду и уничтожу', 62)
        elif 'привет' in message:
            if event.user_id in admin_ids:
                vk.send(event.user_id, 'здравствуйте, хозяин')
            else:
                vk.send(event.user_id, f'и тебя приветствую')
