from ast import literal_eval
from buttons import Buttons
from controllers.controller import Controller
from db.models.settings import Settings


class ControllerSettings(Controller):
    def __init__(self):
        super().__init__()

        self.update_user_buttons()
        self.handlers = [
            {
                'condition': lambda vk, event, user: self.check_payload(event, Buttons.settings),
                'admin': lambda vk, event, user: self.send_buttons(vk, event),
            },
            {
                'condition': lambda vk, event, user: self.check_payload(event, ['block', 'unblock']),
                'admin': lambda vk, event, user: self.action_with_section(vk, event),
            },
        ]

    def send_buttons(self, vk, event):
        body_buttons = [
            button['block'] if Settings.get(button['setting']) else button['unblock']
            for button in self.settings_buttons if button.get('user_button')
        ]

        vk.send(event.user_id, 'as you wish', [
            [Buttons.block_bot if Settings.bot else Buttons.unblock_bot],
            *[[button for button in body_buttons][i:i + 2] for i in range(0, len(body_buttons), 2)],
            [Buttons.to_main]
        ])

    def action_with_section(self, vk, event):
        payload_args = literal_eval(event.payload).get('args')
        button = next(
            button for button in self.settings_buttons
            if payload_args == Buttons.get_args(button['block'])
        )
        if self.__edit_db_enity(button['setting']):
            Settings.change(button['setting'])
            self.update_user_buttons()
            return self.send_buttons(vk, event)
        else:
            raise Exception('проблемс при изменении настройки бота')

    def __edit_db_enity(self, args):
        setting = self.db.session.query(Settings).filter(Settings.name == args).first()
        if not setting:
            return False

        setting.value = not setting.value == 'true'
        self.db.session.commit()
        return True
