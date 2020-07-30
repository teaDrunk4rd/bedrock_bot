from buttons import Buttons
from controllers.controller import Controller


class ControllerStatistics(Controller):
    def __init__(self):
        self.handlers = [
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.admin_stats),
                'privilege': lambda vk, event: vk.send(
                    event.user_id, 'Кол-во проверенных скринов: 0\n'
                                   'Кол-во непроверенных скринов: 0\n'
                                   'Кол-во отклоненных скринов: 0\n'
                                   'Кол-во непроверенных приколов: 0\n' +
                                   ''.join([f'{i + 1}. ФИО vk link: 0\n' for i in range(10)])
                )
            },
        ]
