from buttons import user_button_labels, admin_button_labels
from controllers.controller import Controller
from controllers.controller_base_rules import ControllerBaseRules


class ControllerLowPriority(Controller):
    def __init__(self):
        self.handlers = [
            {
                'condition': lambda vk, event: hasattr(event, 'payload'),
                'main': lambda vk, event: ControllerBaseRules.send_buttons(
                    vk, event, 'ты молодой, шутливый, тебе все легко. это не то. '
                               'это не Чикатило и даже не архивы спецслужб. сюда лучше не лезть',
                    self.main_menu_buttons['main']
                )
            },
            {
                'condition': lambda vk, event: event.text.lower() in user_button_labels,  # TODO: предусмотреть настройки
                'main': lambda vk, event: vk.send(event.user_id, 'чел, используй кнопки')
            },
            {
                'condition': lambda vk, event: event.text.lower() in admin_button_labels,  # TODO: предусмотреть настройки
                'admin': lambda vk, event: vk.send(event.user_id, 'чел, используй кнопки')
            },
            {
                'condition': lambda vk, event: event.text.lower() != '',
                'main': lambda vk, event: vk.send(event.user_id, 'что ты несешь-то вообще?')
            },
        ]
