from vk_api.longpoll import VkEventType
from app import App
from db.models.settings import Settings

app = App()

if Settings.bot:
    app.process_unread_messages()

for event in app.vk.long_pool.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        app.process_new_message(event)
