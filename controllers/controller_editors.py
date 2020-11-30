from buttons import Buttons
from config import Config
from controllers.controller import Controller
from db.db import db
from db.models.role import Role
from db.models.user import User
from decorators.id_getter import id_getter


class ControllerEditors(Controller):
    def __init__(self):
        self.handlers = [
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.editors),
                'admin': lambda vk, event: self.send_buttons(vk, event),
            },
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.add_editor),
                'admin': lambda vk, event: self.add_remove_editor_button(vk, event, Buttons.get_key(Buttons.add_editor)),
            },
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.remove_editor),
                'admin': lambda vk, event: self.add_remove_editor_button(vk, event, Buttons.get_key(Buttons.remove_editor)),
            },
            {
                'condition': lambda vk, event: db.check_user_current_path(event.user_id, Buttons.add_editor),
                'admin': lambda vk, event: self.add_editor(vk, event),
            },
            {
                'condition': lambda vk, event: db.check_user_current_path(event.user_id, Buttons.remove_editor),
                'admin': lambda vk, event: self.remove_editor(vk, event),
            },
        ]

    @staticmethod
    def send_buttons(vk, event):
        editors = db.session.query(User).filter(User.role_id == Role.editor).all()
        editor_names = vk.get_users_names(','.join([f'{editor.user_id}' for editor in editors]))
        message = '\n'.join([
            f'{num + 1}. {editor_names[num]}(vk.com/id{user.user_id})'
            for num, user in enumerate(editors)
        ])

        message = 'назначенные редакторы:\n' + message if message != '' else 'редакторы отсутствуют'
        vk.send(event.user_id, message, [
            [Buttons.add_editor, Buttons.remove_editor],
            [Buttons.to_main]
        ])
        db.update(db.get_user(event.user_id), {User.path: ''})

    @staticmethod
    def add_remove_editor_button(vk, event, path):
        admin = db.get_user(event.user_id)
        db.update(admin, {User.path: path})
        vk.send(event.user_id, f'вводи id в формате "id{event.user_id}"',
                [[Buttons.change_command(Buttons.to_main, Buttons.editors)]])

    @id_getter
    def add_editor(self, vk, event, user_id):
        user = db.get_user(user_id)
        if user_id not in Config.admin_ids and user.first().role_id != Role.editor:
            db.update(user, {'role_id': Role.editor})
            vk.send(user_id, 'тебя выбрали редактором. теперь ты можешь помогать админу с проверкой скринов',
                    self.main_menu_buttons['editor'])
        self.send_buttons(vk, event)

    @id_getter
    def remove_editor(self, vk, event, user_id):
        user = db.get_user(user_id)
        if user_id not in Config.admin_ids and user.first().role_id == Role.editor:
            db.update(user, {'role_id': Role.user})
            vk.send(user_id, 'товарищ редактор, спасибо за помощь. админ теперь справится сам',
                    self.main_menu_buttons['main'])
        self.send_buttons(vk, event)
