from buttons import button_labels, Buttons
from controllers.controller import Controller
from controllers.controller_base_rules import ControllerBaseRules


class ControllerLowPriority(Controller):
    def __init__(self):
        self.handlers = [
            {
                'condition': lambda vk, event: hasattr(event, 'payload'),
                'admin': lambda vk, event: ControllerBaseRules.send_buttons(
                    vk, event, 'стучись разрабу, где-то ошибка',
                    self.main_menu_buttons['admin']
                ),
                'main': lambda vk, event: ControllerBaseRules.send_buttons(
                    vk, event, 'ты молодой, шутливый, тебе все легко. это не то. '
                               'это не Чикатило и даже не архивы спецслужб. сюда лучше не лезть',
                    self.main_menu_buttons['main']
                )
            },
            {
                'condition': lambda vk, event: event.text.lower() == 'exception',
                'admin': lambda vk, event: self.throw_exception()
            },
            {
                'condition': lambda vk, event: event.text.lower() in [
                    Buttons.get_label(Buttons.to_main),
                    *[Buttons.get_label(button) for line in self.main_menu_buttons['main'] for button in line]
                ],
                'main': lambda vk, event: vk.send(event.user_id, 'чел, используй кнопки')
            },
            {
                'condition': lambda vk, event: event.text.lower() in button_labels,
                'admin': lambda vk, event: vk.send(event.user_id, 'чел, используй кнопки')
            },
            {
                'condition': lambda vk, event: event.text.lower() != '',
                'main': lambda vk, event: vk.send(event.user_id, [
                    'что ты несешь-то вообще?',
                    'ну что ты такое говоришь?',
                    'выбрав кнопки в панели, или написав слово "кнопки", ты попадешь в основное меню.'
                ])
            },
        ]

    def throw_exception(self):
        raise Exception('test')
