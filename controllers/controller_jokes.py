from buttons import Buttons
from controllers.controller import Controller


class ControllerJokes(Controller):
    def __init__(self):
        self.handlers = [
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.jokes_check),
                'privilege': lambda vk, event: vk.send(
                    event.user_id,
                    'Ты можешь добавить или отнять баллы за шутку, учитывай, что 1 скрин — 1 балл.\n'
                    'Vk link: ФИО\n'
                    'Прикол:\n'
                    'В купе поезда из Москвы едут русский, китаец и грузин. Китаец звонит по мобильнику, поговорил, выкинул в окно. Русский и грузин - недоумевают. Китаец: "Да у нас в Китае этого г***, чего жалеть-то.."'
                    'Грузин режет арбуз, сьедает кусочек, остальное в окно.Русский и китаец -типа, ты чего? Грузин говорит:"Да у нас этих арбузов как грязи- вот и выкинул".'
                    'Русский смотрит, смотрит... потом встает, и выкидывает в окно Грузин. Китаец: "Зачем??" Русский говорит:"У нас этого добра навалом".',
                    [[Buttons.jokes_good, Buttons.jokes_cringe],
                     [Buttons.jokes_next, Buttons.to_main]]
                )
            },
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.jokes_next),
                'privilege': lambda vk, event: vk.send(
                    event.user_id,
                    'Next:\n'
                    'Vk link: ФИО\n'
                    'Прикол:\n'
                    'Едут в поезде русский, поляк, и немец, и сними девушка. У девушки очень разболелся живот, и она пукнула. Тут поляк сказал:\n'
                    '— Простите у меня очень сильно болит живот, чего-то не то съел в столовой…\n'
                    'Едут дальше. Девушка опять пукнула, тут немец:\n'
                    '— Прошу прощения, переел.\n'
                    'Едут дальше. Русский захотел выйти покурить и сказал:\n'
                    '— Пацаны, если она еще раз пукнет, скажите что это я…\n',
                    [[Buttons.jokes_good, Buttons.jokes_cringe],
                     [Buttons.jokes_next, Buttons.to_main]]
                )
            },
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.jokes_good),
                'privilege': lambda vk, event: vk.send(event.user_id, 'Сколько очков добавить?', [
                    [Buttons.change_command(Buttons.to_main, Buttons.jokes_next)]])
            },
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.jokes_cringe),
                'privilege': lambda vk, event: vk.send(event.user_id, 'Сколько очков отнять?', [
                    [Buttons.change_command(Buttons.to_main, Buttons.jokes_next)]])
            },
        ]
