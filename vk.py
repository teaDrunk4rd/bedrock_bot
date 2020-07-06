import json

from vk_api.longpoll import VkLongPoll


class Vk:
    session = None
    session_api = None
    longpool = None

    def __init__(self, vk_session):
        self.session = vk_session
        self.session_api = self.session.get_api()  # TODO: убрать?
        self.longpool = VkLongPoll(vk_session)  # TODO: убрать?

    def send(self, id, text, buttons=None):
        message = {
            'user_id': id,
            'message': text,
            'random_id': 0
        }
        if buttons:
            message.update({'keyboard': str(
                json.dumps({
                    'one_time': False,
                    'buttons': buttons
                })
            )})
        self.session.method('messages.send', message)

    def send_sticker(self, id, num):
        self.session.method('messages.send', {
            'user_id': id,
            'sticker_id': num,
            'random_id': 0
        })

    def send_message_sticker(self, id, text, sticker_num):
        self.send(id, text)
        self.send_sticker(id, sticker_num)
