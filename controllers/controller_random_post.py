from buttons import Buttons
from controllers.controller import Controller
from db.db import db
import random
from config import Config
from db.models.posts import Posts


class ControllerRandomPost(Controller):
    def __init__(self):
        self.handlers = [
            {
                'condition': lambda vk, event:
                    self.check_payload(event, Buttons.random_post) or
                    'случайный пост' in event.text.lower() and db.check_user_current_path(event.user_id, ''),
                'main': lambda vk, event: self.send_random_post(vk, event)
            }
        ]

    @staticmethod
    def send_random_post(vk, event):
        posts = db.session.query(Posts).first()
        random_post_id = posts.items[random.randint(0, posts.count)]
        vk.send(event.user_id, '', attachments=[f'wall-{Config.group_id}_{random_post_id}'])
