import json
import random
import sys
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll
from media_types import MediaTypes


class Vk:
    session = None
    long_pool = None

    def __init__(self, token):
        self.session = VkApi(token=token)
        self.long_pool = VkLongPoll(self.session)

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

    def get_unread_conversations(self, offset=0, count=200):
        conversations = self.session.method('messages.getConversations', {
            'filter': 'unread',
            'offset': offset,
            'count': count,
            'extended': 0
        })
        return [
                   conversation for conversation in conversations['items']
                   if conversation['conversation']['peer']['type'] != 'chat'
               ], conversations['count']

    def get_message_attachments(self, message_id):
        attachments = self.session.method('messages.getById', {'message_ids': message_id})
        return attachments['items'][0]['attachments'] if attachments['count'] != 0 else None

    def get_user_name(self, user_id):
        try:
            username = self.session.method('users.get', {'user_ids': user_id})
            return f'{username[0]["first_name"]} {username[0]["last_name"]}'
        except:
            return None

    @staticmethod
    def is_photo(event):
        return event.attachments and event.attachments.get('attach1_type') == MediaTypes.photo

    @staticmethod
    def is_audio_msg(event):
        return event.attachments and event.attachments.get('attach1_kind') == MediaTypes.audiomsg

    @staticmethod
    def is_audio(event):
        return event.attachments and event.attachments.get('attach1_type') == MediaTypes.audio
