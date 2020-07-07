import time
from vk_api.vk_api import VkApi
from vk_api.longpoll import VkEventType
from config import Config
from vk import Vk
from answer_rules import AnswerRules


class App:
    @staticmethod
    def process_new_message(event):
        coincidences = [rule for rule in answer_rules.rules if rule['condition'](event)]
        if any(coincidences):
            if event.user_id in Config.admin_ids and 'privilege' in coincidences[0]:
                coincidences[0]['privilege'](vk, event.user_id)
            elif 'main' in coincidences[0]:
                coincidences[0]['main'](vk, event.user_id)
        elif event.text.lower() != '':
            AnswerRules.default_action(vk, event.user_id)

            # while True:
            #     try:
            #         messages = vk.method("messages.getConversations",
            #                              {"offset": 0, "count": 20, "filter": "unanswered"})
            #         if messages["count"] >= 1:
            #             id = messages["items"][0]["last_message"]["from_id"]
            #             body = messages["items"][0]["last_message"]["text"]
            #             if body.lower() == "привет":
            #


vk = Vk(VkApi(token=Config.token))
answer_rules = AnswerRules()
for event in vk.long_pool.listen():
    try:
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            App.process_new_message(event)
    except Exception as e:
        time.sleep(1)  # вести лог в телегу?
