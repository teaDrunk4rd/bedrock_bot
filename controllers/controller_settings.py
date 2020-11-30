from ast import literal_eval
from buttons import Buttons
from controllers.controller import Controller
from db.db import db
from db.models.settings import Settings


class ControllerSettings(Controller):
    __sections_args = [
        Buttons.get_args(Buttons.block_bot),
        Buttons.get_args(Buttons.block_screen),
        Buttons.get_args(Buttons.block_make_joke),
        Buttons.get_args(Buttons.block_essay),
        Buttons.get_args(Buttons.block_random_post),
        Buttons.get_args(Buttons.block_stats),
        Buttons.get_args(Buttons.block_donate),
        Buttons.get_args(Buttons.block_extended_screen_check)
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

    @staticmethod
    def send_buttons(vk, event, message='as you wish'):
        buttons = [
            [Buttons.block_bot if Settings.bot else Buttons.unblock_bot],
            [Buttons.block_screen if Settings.screen else Buttons.unblock_screen,
             Buttons.block_make_joke if Settings.make_joke else Buttons.unblock_make_joke],
            [Buttons.block_essay if Settings.essay else Buttons.unblock_essay,
             Buttons.block_random_post if Settings.random_post else Buttons.unblock_random_post],
            [Buttons.block_stats if Settings.user_stats else Buttons.unblock_stats,
             Buttons.block_donate if Settings.donate else Buttons.unblock_donate],
            [Buttons.block_extended_screen_check if Settings.extended_screen_check else Buttons.unblock_extended_screen_check],
            [Buttons.to_main]
        ]
        vk.send(event.user_id, message, buttons)

    def action_with_section(self, vk, event):
        args = literal_eval(event.payload).get('args')
        if args in self.__sections_args and self.__edit_db_enity(args):
            if args == self.__sections_args[1]:
                Settings.screen = not Settings.screen
            elif args == self.__sections_args[2]:
                Settings.make_joke = not Settings.make_joke
            elif args == self.__sections_args[3]:
                Settings.essay = not Settings.essay
            elif args == self.__sections_args[4]:
                Settings.random_post = not Settings.random_post
            elif args == self.__sections_args[5]:
                Settings.user_stats = not Settings.user_stats
            elif args == self.__sections_args[6]:
                Settings.donate = not Settings.donate
            elif args == self.__sections_args[7]:
                Settings.extended_screen_check = not Settings.extended_screen_check
            elif args == self.__sections_args[0]:
                Settings.bot = not Settings.bot
            else:
                raise Exception('проблемс с args при изменении настроек бота')
            self.update_user_buttons()
            return self.send_buttons(vk, event)
        else:
            raise Exception('проблемс при изменении настройки бота')

    def __edit_db_enity(self, args):
        setting = db.session.query(Settings).filter(Settings.name == args).first()
        if setting:
            setting.value = not setting.value == 'true'
            db.session.commit()
            return True
        else:
            return False
