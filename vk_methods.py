from vk_api.longpoll import VkLongPoll


class Vk:
    session = None
    session_api = None
    longpool = None

    def __init__(self, vk_session):
        self.session = vk_session
        self.session_api = self.session.get_api()
        self.longpool = VkLongPoll(vk_session)

    # def send_message(self, id, text=None, sticker_num=None):
    #     self.session.method('messages.send', {
    #         'user_id': id,
    #         'message': text,
    #         'sticker_id': sticker_num,
    #         'random_id': 0
    #     })

    def send(self, id, text):
        self.session.method('messages.send', {
            'user_id': id,
            'message': text,
            'random_id': 0
        })

    def send_sticker(self, id, num):
        self.session.method('messages.send', {
            'user_id': id,
            'sticker_id': num,
            'random_id': 0
        })

    def send_message_sticker(self, id, text, sticker_num):
        self.send(id, text)
        self.send_sticker(id, sticker_num)
