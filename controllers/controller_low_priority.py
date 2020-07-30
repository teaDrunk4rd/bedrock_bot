from buttons import user_button_labels, admin_button_labels
from controllers.controller import Controller


class ControllerLowPriority(Controller):
    def __init__(self):
        self.handlers = [
            {
                'condition': lambda vk, event: hasattr(event, 'payload'),
                'main': lambda vk, event: vk.send(event.user_id, 'данная функция находятся в разработке')
            },
            {
                'condition': lambda vk, event: event.text.lower() in user_button_labels,
                'main': lambda vk, event: vk.send(event.user_id, 'чел, используй кнопки')
            },
            {
                'condition': lambda vk, event: event.text.lower() in admin_button_labels,
                'privilege': lambda vk, event: vk.send(event.user_id, 'чел, используй кнопки')
            },
            {
                'condition': lambda vk, event: event.text.lower() != '',
                'main': lambda vk, event: vk.send(event.user_id, 'что ты несешь-то вообще?')
            },
        ]
