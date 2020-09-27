import json
import random
from vk_api.vk_api import ApiError
from config import Config
from controllers.controller_action_with_user import ControllerActionWithUser
from controllers.controller_base_rules import ControllerBaseRules
from controllers.controller_jokes import ControllerJokes
from controllers.controller_low_priority import ControllerLowPriority
from controllers.controller_screens import ControllerScreens
from controllers.controller_settings import ControllerSettings
from controllers.controller_statistics import ControllerStatistics
from controllers.controller_random_post import ControllerRandomPost
from controllers.controller_editors import ControllerEditors
from controllers.controller_essay.controller_essay import ControllerEssay
from db.db import db
from db.models.role import Role
from db.models.settings import Settings
from db.models.user import User
from vk import Vk
from multiprocessing.dummy import Process


class App:
    vk = None
    handlers = None

    def __init__(self):
        self.vk = Vk(Config.token)
        ControllerBaseRules().update_user_buttons()
        controller_essay = ControllerEssay()
        self.handlers = [
            *ControllerBaseRules().handlers,
            *ControllerScreens().handlers,
            *ControllerStatistics().handlers,
            *ControllerActionWithUser().handlers,
            *ControllerJokes().handlers,
            *ControllerSettings().handlers,
            *ControllerRandomPost().handlers,
            *ControllerEditors().handlers,
            *controller_essay.handlers,

            *ControllerLowPriority().handlers
        ]
        self.elevator_photos = [457239022, 457239023, 457239024, 457239025, 457239026, 457239027]
        self.elevator_audios = ['322270793_456245436', '322270793_456245435']
        p = Process(target=controller_essay.proceed_essays, args=(self.vk,))
        p.start()

    def process_new_message(self, event):
        try:
            user = db.session.query(User).filter(User.user_id == event.user_id).first()
            if event.user_id in Config.admin_ids or \
                    user.role_id == Role.editor and not user.banned or \
                    Settings.bot and (not user or not user.banned):
                coincidence = next((
                    rule for rule in self.handlers
                    if rule['condition'](self.vk, event) and
                       ('main' in rule or
                        'admin' in rule and event.user_id in Config.admin_ids or
                        'editor' in rule and user.role_id == Role.editor)
                ))
                if coincidence:
                    if 'admin' in coincidence and event.user_id in Config.admin_ids:
                        coincidence['admin'](self.vk, event)
                    elif 'editor' in coincidence and user.role_id == Role.editor:
                        coincidence['editor'](self.vk, event)
                    elif 'main' in coincidence:
                        coincidence['main'](self.vk, event)
        except StopIteration:
            return None
        except Exception as e:
            self.write_error_message(event.user_id)
            self.write_log(self.vk, event.message_id, e)

    def process_unread_messages(self):
        count = 200
        while count == 200:
            conversations, count = self.vk.get_unread_conversations()
            for conversation in conversations:
                self.vk.send(conversation['conversation']['peer']['id'], [
                    'что-то я залип на некоторое время, можешь повторить что ты там говорил?',
                    'извини, что не отвечал, делал свои дела. ну ты знаешь, дела обычного бота бедрока: '
                    'банил всяких гандонов и генерировал мемы. так на чем мы остановились?'
                ])

    @staticmethod
    def write_log(vk, message_id, e):
        print(e)
        if type(e) is ApiError:
            request_params = [
                *[
                    param for param in e.error["request_params"] if
                    param['key'] not in ['message', 'keyboard', 'user_id']
                ], {
                    'keyboard': json.loads(next(iter(
                        [param for param in e.error["request_params"] if param['key'] == 'keyboard']
                    ), None)['value'])
                }
            ]
            msg = f'{e.error["error_code"]}: {e.error["error_msg"]}\n' \
                  f'{json.dumps(request_params, indent=2, ensure_ascii=False)}'
            vk.send(Config.developer, msg, forward_messages=message_id)
        else:
            vk.send(Config.developer, '\n'.join(str(arg) for arg in e.args), forward_messages=message_id)

    def write_error_message(self, user_id):
        elevator_photos = [
            f'photo-{Config.group_id}_{id}' for id in self.elevator_photos
        ]
        elevator_audios = [
            f'audio{id}' for id in self.elevator_audios
        ]
        self.vk.send(
            user_id,
            'что-то пошло не так. попытайтся снова через некоторое время. '
            'если ошибка повторяется несколько раз, то напиши админу',
            attachments=[
                f'{elevator_photos[random.randint(0, len(elevator_photos) - 1)]},'
                f'{elevator_audios[random.randint(0, len(elevator_audios) - 1)]}'
            ]
        )
