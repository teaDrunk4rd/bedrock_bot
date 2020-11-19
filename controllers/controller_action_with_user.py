from buttons import Buttons
from config import Config
from controllers.controller import Controller
from controllers.controller_statistics import ControllerStatistics
from db.db import db
from db.models.role import Role
from db.models.user import User
from decorators.scores_getter import scores_getter
from decorators.id_getter import id_getter


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
                    db.check_user_current_path(event.user_id, f'{Buttons.get_key(Buttons.action_with_user)}: id', in_arg=True),
                'admin': lambda vk, event: self.ban_unban_user(vk, event, ban=True)
            },
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.unban_user) and
                    db.check_user_current_path(event.user_id, f'{Buttons.get_key(Buttons.action_with_user)}: id', in_arg=True),
                'admin': lambda vk, event: self.ban_unban_user(vk, event, ban=False)
            },
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.add_scores),
                'admin': lambda vk, event:
                    self.add_remove_scores_button(vk, event, Buttons.add_scores, 'сколько очков добавить?')
            },
            {
                'condition': lambda vk, event:
                    db.check_user_current_path(event.user_id, f'{Buttons.get_key(Buttons.add_scores)}: id', in_arg=True),
                'admin': lambda vk, event: self.add_scores(vk, event)
            },
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.remove_scores),
                'admin': lambda vk, event:
                    self.add_remove_scores_button(vk, event, Buttons.remove_scores, 'сколько очков отнять?')
            },
            {
                'condition': lambda vk, event:
                    db.check_user_current_path(event.user_id, f'{Buttons.get_key(Buttons.remove_scores)}: id', in_arg=True),
                'admin': lambda vk, event: self.remove_scores(vk, event)
            },
        ]

    @staticmethod
    def action_with_user_button(vk, event):
        admin = db.get_user(event.user_id)
        db.update(admin, {User.path: Buttons.get_key(Buttons.action_with_user)})
        vk.send(event.user_id, f'вводи id в формате "id{event.user_id}"', [[Buttons.to_main]])

    @id_getter
    def action_with_user_id(self, vk, event, user_id):
        user = db.session.query(User).filter(User.user_id == user_id).first()
        ControllerActionWithUser.__send_user_stats(vk, event.user_id, user)
        admin = db.get_user(event.user_id)
        db.update(admin, {User.path: f'{Buttons.get_key(Buttons.action_with_user)}: id{user_id}'})

    @staticmethod
    def __send_user_stats(vk, admin_id, user):
        if user:
            role = 'Редактор\n' if user.role_id == Role.editor else ''
            message = f'{vk.get_users_names(user.user_id)}\n' \
                      f'{role}' \
                      f'Статус: {user.get_status()}\n' \
                      f'{ControllerStatistics.get_user_stats(user.user_id)}'
            buttons = [
                [Buttons.add_scores, Buttons.unban_user if user.banned else Buttons.ban_user],
                [Buttons.remove_scores, Buttons.to_main]
            ]
            vk.send(admin_id, message, buttons)
        else:
            vk.send(admin_id, 'чел с таким id не взаимодействовал пока с ботом')

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

    @scores_getter
    def add_scores(self, vk, event, scores):
        admin = db.get_user(event.user_id)
        user_id = int(admin.first().path.split(': ')[1].replace('id', ''))
        user = db.session.query(User).filter(User.user_id == user_id).first()
        user.scores = user.scores + scores
        db.session.commit()
        vk.send(user.user_id,
                f'поздравляю, тебе добавили {scores} {self.plural_form(scores, "очко", "очка", "очков")}\n'
                f'на данный момент у тебя {user.scores} {self.plural_form(user.scores, "очко", "очка", "очков")}')
        ControllerActionWithUser.__send_user_stats(vk, event.user_id, user)
        admin = db.get_user(event.user_id)
        db.update(admin, {User.path: f'{Buttons.get_key(Buttons.action_with_user)}: id{user.user_id}'})

    @scores_getter
    def remove_scores(self, vk, event, scores):
        admin = db.get_user(event.user_id)
        user_id = int(admin.first().path.split(': ')[1].replace('id', ''))
        user = db.session.query(User).filter(User.user_id == user_id).first()
        user.scores = user.scores - scores
        db.session.commit()
        vk.send(user.user_id,
                f'у тебя отняли {scores} {self.plural_form(scores, "очко", "очка", "очков")}\n'
                f'на данный момент у тебя {user.scores} {self.plural_form(user.scores, "очко", "очка", "очков")}')
        ControllerActionWithUser.__send_user_stats(vk, event.user_id, user)
        admin = db.get_user(event.user_id)
        db.update(admin, {User.path: f'{Buttons.get_key(Buttons.action_with_user)}: id{user.user_id}'})
