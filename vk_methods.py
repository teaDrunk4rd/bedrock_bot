from vk_api.longpoll import VkLongPoll


class Vk:
    vk_session = None
    session_api = None
    longpool = None

    def __init__(self, vk_session):
        self.vk_session = vk_session
        self.session_api = self.vk_session.get_api()
        self.longpool = VkLongPoll(vk_session)

    def send(self, id, text):
        self.vk_session.method('messages.send', {
            'user_id': id,
            'message': text,
            'random_id': 0
        })
