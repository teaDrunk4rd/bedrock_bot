import json
import random
import sys
from vk_api.longpoll import VkLongPoll
from media_types import MediaTypes


class Vk:
    session = None
    long_pool = None

    def __init__(self, vk_session):
        self.session = vk_session
        self.long_pool = VkLongPoll(vk_session)

    def send(self, id, text, buttons=None, forward_messages=None, attachments=None):
        if type(text) is list:
            text = text[random.randint(0, len(text) - 1)]
        message = {
            'user_id': id,
            'message': text,
            'forward_messages': forward_messages,
            'attachment': attachments,
            'random_id': random.randint(0, sys.maxsize * sys.maxsize * 2)
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
            'random_id': random.randint(0, sys.maxsize * sys.maxsize * 2)
        })

    def send_message_sticker(self, id, text, sticker_num):
        self.send(id, text)
        self.send_sticker(id, sticker_num)

    # def get_last_messages(self, id, count=2):
    #     return self.session.method('messages.getHistory', {
    #         'count': count,
    #         'user_id': id
    #     })['items']
    #
    # def check_previous_bot_message(self, id, text):
    #     return any([message for message in self.get_last_messages(id) if message['text'] == text and message['from_id'] != id])

    @staticmethod
    def is_photo(event):
        return event.attachments and event.attachments.get('attach1_type') == MediaTypes.photo

    @staticmethod
    def is_audio_msg(event):
        return event.attachments and event.attachments.get('attach1_kind') == MediaTypes.audiomsg
