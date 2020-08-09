import json
from vk_api.vk_api import VkApi, ApiError
from config import Config
from controllers.controller_action_with_user import ControllerActionWithUser
from controllers.controller_base_rules import ControllerBaseRules
from controllers.controller_jokes import ControllerJokes
from controllers.controller_low_priority import ControllerLowPriority
from controllers.controller_screens import ControllerScreens
from controllers.controller_settings import ControllerSettings
from controllers.controller_statistics import ControllerStatistics
from controllers.controller_random_post import ControllerRandomPost
from db.db import db
from db.models.user import User
from vk import Vk


class App:
    vk = None
    handlers = None

    def __init__(self):
        self.vk = Vk(VkApi(token=Config.token))
        ControllerBaseRules().update_user_buttons()
        self.handlers = [
            *ControllerBaseRules().handlers,
            *ControllerScreens().handlers,
            *ControllerStatistics().handlers,
            *ControllerActionWithUser().handlers,
            *ControllerJokes().handlers,
            *ControllerSettings().handlers,
            *ControllerRandomPost().handlers,

            *ControllerLowPriority().handlers
        ]

    def process_new_message(self, event):
        try:
            user = db.session.query(User).filter(User.user_id == event.user_id).first()
            if not user or event.user_id in Config.admin_ids or not user.banned:
                coincidence = next((
                    rule for rule in self.handlers
                    if rule['condition'](self.vk, event) and ('main' in rule or 'admin' in rule and event.user_id in Config.admin_ids)
                ))
                if coincidence:
                    if 'admin' in coincidence and event.user_id in Config.admin_ids:
                        coincidence['admin'](self.vk, event)
                    elif 'main' in coincidence:
                        coincidence['main'](self.vk, event)
        except StopIteration:
            return None
        # except Exception as e:
        #     App.write_log(self.vk, event.message_id, e)

    @staticmethod
    def write_log(vk, message_id, e):
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
            vk.send(Config.log_receiver, msg, forward_messages=message_id)
        else:
            vk.send(Config.log_receiver, '\n'.join(e.args), forward_messages=message_id)
