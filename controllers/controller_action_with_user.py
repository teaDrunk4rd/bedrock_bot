from buttons import Buttons
from config import Config
from controllers.controller import Controller
from controllers.controller_statistics import ControllerStatistics
from db.db import db
from db.models.user import User


class ControllerActionWithUser(Controller):
    def __init__(self):
        self.handlers = [
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.action_with_user),
                'admin': lambda vk, event: self.action_with_user_button(vk, event)
            },
            {
                'condition': lambda vk, event: db.check_user_current_path(event.user_id, Buttons.action_with_user),
                'admin': lambda vk, event: self.action_with_user_id(vk, event)
            },
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.ban_user) and
                    db.check_user_current_path(event.user_id, f'{Buttons.get_key(Buttons.action_with_user)}: id', True),
                'admin': lambda vk, event: self.ban_unban_user(vk, event, ban=True)
            },
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.unban_user) and
                    db.check_user_current_path(event.user_id, f'{Buttons.get_key(Buttons.action_with_user)}: id', True),
                'admin': lambda vk, event: self.ban_unban_user(vk, event, ban=False)
            },
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.add_scores),
                'admin': lambda vk, event:
                    self.add_remove_scores_button(vk, event, Buttons.add_scores, 'сколько очков добавить?')
            },
            {
                'condition': lambda vk, event: db.check_user_current_path(event.user_id, f'{Buttons.get_key(Buttons.add_scores)}: id', True),
                'admin': lambda vk, event: self.add_remove_scores(vk, event, action=lambda x, y: x + y)
            },
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.remove_scores),
                'admin': lambda vk, event:
                    self.add_remove_scores_button(vk, event, Buttons.remove_scores, 'сколько очков отнять?')
            },
            {
                'condition': lambda vk, event: db.check_user_current_path(event.user_id, f'{Buttons.get_key(Buttons.remove_scores)}: id', True),
                'admin': lambda vk, event: self.add_remove_scores(vk, event, action=lambda x, y: x - y)
            },
        ]

    @staticmethod
    def action_with_user_button(vk, event):
        admin = db.get_user(event.user_id)
        db.update(admin, {User.path: Buttons.get_key(Buttons.action_with_user)})
        vk.send(event.user_id, f'вводи id в формате "id{event.user_id}"', [[Buttons.to_main]])

    @staticmethod
    def action_with_user_id(vk, event):
        try:
            user_id = int(event.text.replace('id', ''))
            user = db.session.query(User).filter(User.user_id == user_id).first()
            ControllerActionWithUser.__send_user_stats(vk, event.user_id, user)
            admin = db.get_user(event.user_id)
            db.update(admin, {User.path: f'{Buttons.get_key(Buttons.action_with_user)}: id{user.user_id}'})
        except ValueError:
            vk.send(event.user_id, 'ты ввел id не в том формате')

    @staticmethod
    def __send_user_stats(vk, admin_id, user):
        if user:
            message = f'{vk.get_user_name(user.user_id)}\n' \
                      f'Статус: {user.get_status()}\n' \
                      f'{ControllerStatistics.get_user_stats(user.user_id)}'
            buttons = [
                [Buttons.add_scores, Buttons.unban_user if user.banned else Buttons.ban_user],
                [Buttons.remove_scores, Buttons.to_main]
            ]
            vk.send(admin_id, message, buttons)
        else:
            vk.send(user.user_id, 'чел с таким id не взаимодействовал пока с ботом')

    @staticmethod
    def ban_unban_user(vk, event, ban):
        admin = db.session.query(User).filter(User.user_id == event.user_id).first()
        user_id = int(admin.path.split(': ')[1].replace('id', ''))
        if user_id not in Config.admin_ids:
            user = db.session.query(User).filter(User.user_id == user_id).first()
            user.banned = ban
            db.session.commit()
            ControllerActionWithUser.__send_user_stats(vk, event.user_id, user)
        else:
            vk.send(event.user_id, 'ты кто такой, чтобы делать это?')

    @staticmethod
    def add_remove_scores_button(vk, event, button, message):
        admin = db.get_user(event.user_id)
        user_id = int(admin.first().path.split(': ')[1].replace('id', ''))
        db.update(admin, {User.path: f'{Buttons.get_key(button)}: id{user_id}'})
        vk.send(event.user_id, message, [[Buttons.change_command(Buttons.to_main, Buttons.action_with_user)]])

    @staticmethod
    def add_remove_scores(vk, event, action):
        try:
            scores = int(event.text.replace('id', ''))
            admin = db.get_user(event.user_id)
            user_id = int(admin.first().path.split(': ')[1].replace('id', ''))
            user = db.session.query(User).filter(User.user_id == user_id).first()
            user.scores = action(user.scores, scores)
            db.session.commit()
            ControllerActionWithUser.__send_user_stats(vk, event.user_id, user)
            admin = db.get_user(event.user_id)
            db.update(admin, {User.path: f'{Buttons.get_key(Buttons.action_with_user)}: id{user.user_id}'})
        except ValueError:
            vk.send(event.user_id, 'мне нужно число очков')
