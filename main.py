import vk_api
from vk_api.longpoll import VkEventType
from config import Config
from vk_methods import Vk

admin_ids = [132228887, 322270793]
bad_words = ['ебал', 'гандон', 'пидор', 'хуй', 'соси', 'мразь', 'залупа', 'жопа', 'член', 'еблан', 'вагина', 'долбаеб']
answer_rules = [
    {
        'condition': lambda id, message: 'ты пидор' in message,
        'main': lambda id: vk.send_message_sticker(id, 'а может ты пидор?', 49)
    },
    {
        'condition': lambda id, message: any([abuse for abuse in bad_words if abuse in message]),
        'privilege': lambda id: vk.send(id, 'хозяин, не нужно мне такие гадости писать, мне неприятно. лучше склепайте новых мемов'),
        'main': lambda id: vk.send_message_sticker(id, f'мразь, я знаю что ты сидишь с id {id}, я тебя найду и уничтожу', 62)
    },
    {
        'condition': lambda id, message: 'привет' in message,
        'privilege': lambda id: vk.send(id, 'здравствуйте, хозяин'),
        'main': lambda id: vk.send(id, f'и тебя приветствую')
    },
]
vk = Vk(vk_api.VkApi(token=Config.token))
# TODO: привязать к юзеру поле, отмечающее его сквернословие и общаться подобающим образом или требовать извинения
for event in vk.longpool.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        message = event.text.lower()
        coincidences = [rule for rule in answer_rules if rule['condition'](event.user_id, message)]
        if any(coincidences):
            if event.user_id in admin_ids and 'privilege' in coincidences[0]:
                coincidences[0]['privilege'](event.user_id)
            else:
                coincidences[0]['main'](event.user_id)
