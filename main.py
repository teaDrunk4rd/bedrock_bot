import time
import vk_api
from vk_api.longpoll import VkEventType
from config import Config
from vk_methods import Vk
from answer_rules import answer_rules, default_action


vk = Vk(vk_api.VkApi(token=Config.token))
# TODO: привязать к юзеру поле, отмечающее его сквернословие и общаться подобающим образом или требовать извинения
for event in vk.longpool.listen():
    try:
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            coincidences = [rule for rule in answer_rules if rule['condition'](event)]
            if any(coincidences):
                if event.user_id in Config.admin_ids and 'privilege' in coincidences[0]:
                    coincidences[0]['privilege'](vk, event.user_id)
                elif 'main' in coincidences[0]:
                    coincidences[0]['main'](vk, event.user_id)
            elif event.text.lower() != '':
                default_action(vk, event.user_id)
    except Exception as e:
        time.sleep(2)  # вести лог?
