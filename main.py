from vk_api.vk_api import VkApi, ApiError
from vk_api.longpoll import VkEventType
from config import Config
from vk import Vk
from answer_rules import AnswerRules
import json


class App:
    vk = None
    answer_rules = None

    def __init__(self):
        self.vk = Vk(VkApi(token=Config.token))
        self.answer_rules = AnswerRules()

    def process_new_message(self, event):
        try:
            coincidence = next((
                rule for rule in self.answer_rules.rules
                if rule['condition'](self.vk, event) and ('main' in rule or 'privilege' in rule and event.user_id in Config.admin_ids)
            ))
            if coincidence:
                if 'privilege' in coincidence and event.user_id in Config.admin_ids:
                    coincidence['privilege'](self.vk, event)
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


app = App()
for event in app.vk.long_pool.listen():
    if event.type == VkEventType.MESSAGE_NEW and event.to_me:
        app.process_new_message(event)
