from vk_api.vk_api import VkApi
from vk_api.longpoll import VkEventType
from config import Config
from vk import Vk
from answer_rules import AnswerRules, answer_rules


class App:
    @staticmethod
    def process_new_message(event):
        coincidences = [rule for rule in answer_rules.rules if rule['condition'](vk, event)]
        if any(coincidences):
            if event.user_id in Config.admin_ids and 'privilege' in coincidences[0]:
                coincidences[0]['privilege'](vk, event)
            elif 'main' in coincidences[0]:
                coincidences[0]['main'](vk, event)


vk = Vk(VkApi(token=Config.token))
for event in vk.long_pool.listen():
    try:
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            App.process_new_message(event)
    except Exception as e:
        AnswerRules.write_log(vk, event, e)
