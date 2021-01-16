from buttons import Buttons
from controllers.controller import Controller
from db.models.settings import Settings
from db.models.user import User


class ControllerCallAdmin(Controller):
    def __init__(self):
        super().__init__()

        self.handlers = [
            {
                'condition': lambda vk, event, user: (
                    self.check_payload(event, Buttons.call_admin) or
                    self.any_equal([
                       'вызываю админа',
                       'вызвать админа',
                       'админ приди'
                    ], event.text.lower())
                ) and user.compare_path('')
                    and self.check_access(Settings.call_admin, event.user_id),
                'main': lambda vk, event, user: self.call_admin(vk, event, user)
            },
            {
                'condition': lambda vk, event, user: self.any_equal([
                       'вызываю бота',
                       'вызвать бота',
                       'бот приди'
                    ], event.text.lower()) and user.compare_path(Buttons.call_admin),
                'main': lambda vk, event, user: self.call_bot(vk, event, user),
                'special': True
            },
        ]

    def call_admin(self, vk, event, user):
        self.db.update(user, {User.path: Buttons.get_key(Buttons.call_admin)})
        vk.send(
            event.user_id,
            'понял, позову админа. если захочешь снова разговаривать с бездушным роботом пиши "вызываю бота"'
        )

    def call_bot(self, vk, event, user):
        self.db.update(user, {User.path: ''})
        vk.send(
            event.user_id,
            'привет, привет. давно не разговаривали, я уже успел соскучаться по тебе, солнышко T-T'
        )
