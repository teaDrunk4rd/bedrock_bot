from ast import literal_eval
from buttons import Buttons
from controllers.controller import Controller
from db.db import db
from db.models.settings import Settings


class ControllerSettings(Controller):
    __buttons = [
        {
            'block': Buttons.block_bot,
            'unblock': Buttons.unblock_bot,
            'setting': 'bot'
        },
        {
            'block': Buttons.block_make_joke,
            'unblock': Buttons.unblock_make_joke,
            'setting': 'make_joke'
        },
        {
            'block': Buttons.block_stats,
            'unblock': Buttons.unblock_stats,
            'setting': 'user_stats'
        },
        {
            'block': Buttons.block_essay,
            'unblock': Buttons.unblock_essay,
            'setting': 'essay'
        },
        {
            'block': Buttons.block_random_post,
            'unblock': Buttons.unblock_random_post,
            'setting': 'random_post'
        },
        {
            'block': Buttons.block_donate,
            'unblock': Buttons.unblock_donate,
            'setting': 'donate'
        },
    ]

    def __init__(self):
        self.handlers = [
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.settings),
                'admin': lambda vk, event: self.send_buttons(vk, event),
            },
            {
                'condition': lambda vk, event: self.check_payload(event, ['block', 'unblock']),
                'admin': lambda vk, event: self.action_with_section(vk, event),
            },
        ]

    def send_buttons(self, vk, event):
        body_buttons = [
            button['block'] if Settings.get(button['setting']) else button['unblock']
            for button in self.__buttons if button['setting'] != 'bot'
        ]

        vk.send(event.user_id, 'as you wish', [
            [Buttons.block_bot if Settings.bot else Buttons.unblock_bot],
            *[[button for button in body_buttons][i:i + 2] for i in range(0, len(body_buttons), 2)],
            [Buttons.to_main]
        ])

    def action_with_section(self, vk, event):
        try:
            button = next(
                button for button in self.__buttons
                if literal_eval(event.payload).get('args') == Buttons.get_args(button['block'])
            )
            Settings.change(button['setting'])
            self.update_user_buttons()
            return self.send_buttons(vk, event)
        except:
            raise Exception('проблемс при изменении настройки бота')

    def __edit_db_enity(self, args):
        setting = db.session.query(Settings).filter(Settings.name == args).first()
        if not setting:
            return False

        setting.value = not setting.value == 'true'
        db.session.commit()
        return True
