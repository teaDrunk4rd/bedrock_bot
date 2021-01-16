from buttons import Buttons
from controllers.controller import Controller
from db.db import db
from db.models.settings import Settings
from db.models.user import User


class ControllerCallAdmin(Controller):
    def __init__(self):
        self.handlers = [
            {
                'condition': lambda vk, event: (
                    self.check_payload(event, Buttons.call_admin) or
                    self.any_equal([
                       'вызываю админа',
                       'вызвать админа',
                       'админ приди'
                    ], event.text.lower())
                ) and db.check_user_current_path(event.user_id, '')
                    and self.check_access(Settings.call_admin, event.user_id),
                'main': lambda vk, event: self.call_admin(vk, event)
            },
            {
                'condition': lambda vk, event: self.any_equal([
                       'вызываю бота',
                       'вызвать бота',
                       'бот приди'
                    ], event.text.lower()) and db.check_user_current_path(event.user_id, Buttons.call_admin),
                'main': lambda vk, event: self.call_bot(vk, event),
                'special': True
            },
        ]

    @staticmethod
    def call_admin(vk, event):
        user = db.session.query(User).filter(User.user_id == event.user_id)
        db.update(user, {User.path: Buttons.get_key(Buttons.call_admin)})
        vk.send(
            event.user_id,
            'понял, позову админа. если захочешь снова разговаривать с бездушным роботом пиши "вызываю бота"'
        )

    @staticmethod
    def call_bot(vk, event):
        user = db.session.query(User).filter(User.user_id == event.user_id)
        db.update(user, {User.path: ''})
        vk.send(
            event.user_id,
            'привет, привет. давно не разговаривали, я уже успел соскучаться по тебе, солнышко T-T'
        )
