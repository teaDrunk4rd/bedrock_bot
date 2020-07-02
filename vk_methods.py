import json

from vk_api.longpoll import VkLongPoll


def get_button(label, color, payload=''):
    return {
        'action': {
            'type': 'text',
            'payload': json.dumps(payload),
            'label': label
        },
        'color': color
    }

class Vk:
    session = None
    session_api = None
    longpool = None

    def __init__(self, vk_session):
        self.session = vk_session
        self.session_api = self.session.get_api()
        self.longpool = VkLongPoll(vk_session)

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
                    'buttons': [[get_button(button[0], button[1]) for button in button_line] for button_line in buttons]
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
