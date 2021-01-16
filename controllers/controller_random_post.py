from buttons import Buttons
from controllers.controller import Controller
import random
from config import Config
from db.models.posts import Posts
from db.models.settings import Settings


class ControllerRandomPost(Controller):
    def __init__(self):
        super().__init__()

        self.handlers = [
            {
                'condition': lambda vk, event, user: (
                    self.check_payload(event, Buttons.random_post) or
                    self.any_equal([
                        'случайный пост',
                        'рандомный пост',
                        'пост',
                        'кинь пост'
                    ], event.text.lower())
                ) and user.compare_path('') and self.check_access(Settings.random_post, event.user_id),
                'main': lambda vk, event, user: self.send_random_post(vk, event)
            }
        ]

    def send_random_post(self, vk, event):
        posts = self.db.session.query(Posts).first()
        random_post_id = posts.items[random.randint(0, posts.count - 1)]
        vk.send(event.user_id, '', attachments=[f'wall-{Config.group_id}_{random_post_id}'])
