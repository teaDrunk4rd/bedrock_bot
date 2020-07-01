import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from config import Config
from vk_methods import Vk

abuses = ['ебал', 'гандон', 'пидор', 'хуй', 'соси', 'мразь']

vk = Vk(vk_api.VkApi(token=Config.token))

for event in vk.longpool.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        message = event.text.lower()
        if any([abuse for abuse in abuses if abuse in message]):
            if event.user_id == 132228887:
                vk.send(event.user_id, 'Хозяин, не нужно мне такие гадости писать, мне неприятно. Лучше склепайте новых мемов.')
            else:
                vk.send(event.user_id, f'Мразь, я знаю что ты сидишь с id {event.user_id}, я тебя найду и уничтожу.')
        elif 'привет' in message:
            if event.user_id == 132228887:
                vk.send(event.user_id, 'Здравствуйте, хозяин.')
            else:
                vk.send(event.user_id, f'И тебя приветствую.')
