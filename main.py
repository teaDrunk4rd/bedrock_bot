from vk_api.longpoll import VkEventType
from app import App

app = App()
for event in app.vk.long_pool.listen():  # TODO: обработка непрочитанных сообщений: что-то я залип на некоторое время, можешь повторить что ты говорил там?
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        app.process_new_message(event)
