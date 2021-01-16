from buttons import Buttons
from config import Config
from controllers.controller import Controller
from controllers.controller_statistics import ControllerStatistics
from db.models.user import User
from decorators.id_getter import id_getter


class ControllerActionWithUser(Controller):
    def __init__(self):
        super().__init__()

        self.handlers = [
            {
                'condition': lambda vk, event, user: self.check_payload(event, Buttons.action_with_user),
                'admin': lambda vk, event, user: self.action_with_user_button(vk, event, user)
            },
            {
                'condition': lambda vk, event, user: user.compare_path(Buttons.action_with_user),
                'admin': lambda vk, event, user: self.action_with_user_id(vk, event, user)
            },
            {
                'condition': lambda vk, event, user: self.check_payload(event, Buttons.ban_user) and
                    user.compare_path(f'{Buttons.get_key(Buttons.action_with_user)}: id', in_arg=True),
                'admin': lambda vk, event, user: self.ban_unban_user(vk, event, user, ban=True)
            },
            {
                'condition': lambda vk, event, user: self.check_payload(event, Buttons.unban_user) and
                    user.compare_path(f'{Buttons.get_key(Buttons.action_with_user)}: id', in_arg=True),
                'admin': lambda vk, event, user: self.ban_unban_user(vk, event, user, ban=False)
            },
        ]

    def action_with_user_button(self, vk, event, admin):
        self.db.update(admin, {User.path: Buttons.get_key(Buttons.action_with_user)})
        vk.send(event.user_id, f'вводи id в формате "id{event.user_id}"', [[Buttons.to_main]])

    @id_getter
    def action_with_user_id(self, vk, event, admin, user_id):
        user = self.db.session.query(User).filter(User.user_id == user_id).first()
        self.__send_user_stats(vk, event.user_id, user)
        self.db.update(admin, {User.path: f'{Buttons.get_key(Buttons.action_with_user)}: id{user_id}'})

    def __send_user_stats(self, vk, admin_id, user):
        if user:
            message = f'{vk.get_users_names(user.user_id)[0]}\n' \
                      f'Статус: {user.get_status()}\n' \
                      f'{ControllerStatistics.get_user_stats(self.db, user.user_id)}'
            buttons = [
                [Buttons.unban_user if user.banned else Buttons.ban_user, Buttons.to_main]
            ]
            vk.send(admin_id, message, buttons)
        else:
            vk.send(admin_id, 'чел с таким id не взаимодействовал пока с ботом')

    def ban_unban_user(self, vk, event, admin, ban):
        user_id = int(admin.path.split(': ')[1].replace('id', ''))
        if user_id not in Config.admin_ids:
            user = self.db.session.query(User).filter(User.user_id == user_id).first()
            user.banned = ban
            self.db.session.commit()
            self.__send_user_stats(vk, event.user_id, user)
        else:
            vk.send(event.user_id, 'ты кто такой, чтобы делать это?')
