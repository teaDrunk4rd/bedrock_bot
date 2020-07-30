from buttons import Buttons
from controllers.controller import Controller


class ControllerActionWithUser(Controller):
    def __init__(self):
        self.handlers = [
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.action_with_user),
                'privilege': lambda vk, event: vk.send(
                    event.user_id, '(Будут показываться кнопки очков и только бана или только разбана)')
                    #Controller.__action_with_users_buttons)
            },
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.ban_user),
                'privilege': lambda vk, event: vk.send(event.user_id, 'Забанен')
            },
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.unban_user),
                'privilege': lambda vk, event: vk.send(event.user_id, 'Разбанен')
            },
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.add_scores),
                'privilege': lambda vk, event: vk.send(
                    event.user_id, 'Сколько очков добавить?',
                    [[Buttons.change_command(Buttons.to_main, Buttons.action_with_user)]])
            },
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.remove_scores),
                'privilege': lambda vk, event: vk.send(
                    event.user_id, 'Сколько очков отнять?',
                    [[Buttons.change_command(Buttons.to_main, Buttons.action_with_user)]])
            },
        ]
