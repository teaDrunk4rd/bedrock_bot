import time
from vk_api.vk_api import VkApi
from vk_api.longpoll import VkEventType
from config import Config
from vk import Vk
from answer_rules import answer_rules, default_action


class App:
    @staticmethod
    def process_new_message(event):
        coincidences = [rule for rule in answer_rules if rule['condition'](event)]
        if any(coincidences):
            if event.user_id in Config.admin_ids and 'privilege' in coincidences[0]:
                coincidences[0]['privilege'](vk, event.user_id)
            elif 'main' in coincidences[0]:
                coincidences[0]['main'](vk, event.user_id)
        elif event.text.lower() != '':
            default_action(vk, event.user_id)


vk = Vk(VkApi(token=Config.token))
for event in vk.longpool.listen():
    try:
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            App.process_new_message(event)
    except Exception as e:
        time.sleep(2)  # вести лог в телегу?
