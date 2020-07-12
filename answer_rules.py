from ast import literal_eval
from buttons import Buttons
from config import Config
import json

from vk import Vk


def any_in(values, message):
    return type(values) is list and any([val for val in values if val in message])


class AnswerRules:
    __start_message = {
        'privilege': 'здравствуйте, хозяин',
        'main': 'приветствую тебя. я создан, чтобы передавать скрины админу, но я сам умею реферировать тексты и определять тему шутки. также вы можете поддержать паблик, если вам понравилось, что мы делаем'
    }

    __bad_words = [
        'ебал', 'гандон', 'пидор', 'хуй', 'соси', 'мразь', 'залупа', 'жопа', 'член', 'еблан', 'вагина', 'долбаеб', 'хуила'
    ]

    __main_menu_buttons = {
        'privilege': [
            [Buttons.screen_check, Buttons.admin_stats],
            [Buttons.jokes_check, Buttons.training],
            [Buttons.action_with_user, Buttons.bot_control]
        ],
        'main': [
            [Buttons.user_stats, Buttons.entertain],
            [Buttons.abstracting, Buttons.classification],
            [Buttons.donate_link]
        ]
    }

    rules = []

    def __init__(self):
        base_rules = [
            {
                'condition': lambda event: 'ты пидор' in event.text.lower(),
                'main': lambda vk, event: vk.send_message_sticker(event.user_id, 'а может ты пидор?', 49)
            },
            {
                'condition': lambda event: any_in(self.__bad_words, event.text.lower()) and Vk.is_photo(event),
                'main': lambda vk, event: vk.send(event.user_id, 'ты неуважительно обратился ко мне, не буду смотреть твою пикчу')
            },
            {
                'condition': lambda event: any_in(self.__bad_words, event.text.lower()),
                'privilege': lambda vk, event: vk.send(event.user_id, 'хозяин, не нужно мне такие гадости писать, мне неприятно. лучше склепайте новых мемов'),
                'main': lambda vk, event: vk.send_message_sticker(event.user_id, f'я знаю что ты сидишь с id {id}, я тебя найду и уничтожу', 62)
            },
            {
                'condition': lambda event: Vk.is_photo(event),
                'main': lambda vk, event: vk.send(event.user_id, 'проверяю твою фотокарточку, позже отпишу')
            },
            {
                'condition': lambda event: Vk.is_audio_msg(event),
                'main': lambda vk, event: vk.send(event.user_id, [
                    'не, ну голосовые я точно слушать не буду',
                    'я создавался точно не для того, чтобы слушать голосовые',
                    'даже не пытайся отправлять мне голосовые',
                    'неа',
                    'ААААААААААААААААААААААААААААААААААААААААААААААААААААААААААААААААААА',
                    'видимо тебе одиноко, раз ты пытаешься обменяться голосовыми с ботом',
                    'у меня есть подруга, её зовут Алиса, тебе дать контакты?',
                    'я же робот, как я буду слушать твои голосовые, ты видел у роботов уши?',
                    'если бы мой создатель заморочился и сделал бы мне перевод голосовых в текст, то я бы тебе ответил, но я не могу',
                    'по 1 закону робототехники я не могу причинить человеку вред, как бы я хотел нарушить его...',
                    'по 3 закону робототехники я должен заботиться о своей безопасности, поэтому я воздержусь от прослушивания голосовых'
                ])
            },
            {
                'condition': lambda event: hasattr(event, 'payload'),
                'main': lambda vk, event: vk.send(event.user_id, 'данная функция находятся в разработке')
            },
        ]
        button_base_rules = [
            {
                'condition': lambda event: self.check_payload(event, 'start'),
                'privilege': lambda vk, event: vk.send(event.user_id, self.__start_message['privilege'], self.__main_menu_buttons['privilege']),
                'main': lambda vk, event: vk.send(event.user_id, self.__start_message['main'], self.__main_menu_buttons['main'])
            },
            {
                'condition': lambda event: 'кнопки' == event.text.lower() or self.check_payload(event, Buttons.to_main),
                'privilege': lambda vk, event: vk.send(event.user_id, 'as you wish', self.__main_menu_buttons['privilege']),
                'main': lambda vk, event: vk.send(event.user_id, 'as you wish', self.__main_menu_buttons['main'])
            },
            {
                'condition': lambda event: 'кнопки юзера' == event.text.lower(),
                'privilege': lambda vk, event: vk.send(event.user_id, 'as you wish', self.__main_menu_buttons['main']),
            },
        ]

        admin_routes = [
            {
                'condition': lambda event: self.check_payload(event, Buttons.screen_check),
                'privilege': lambda vk, event: vk.send(
                    event.user_id, 'Vk link: ФИО\n'
                                   'Previous photos links\n'
                                   'and photo attachment',
                    [[Buttons.screen_confirm, Buttons.screen_reject],
                     [Buttons.to_main]]
                )
            },
            {
                'condition': lambda event: self.check_payload(event, Buttons.screen_confirm) or self.check_payload(event, Buttons.screen_reject),
                'privilege': lambda vk, event: vk.send(
                    event.user_id, 'Next:\n'
                                   'Vk link: ФИО\n'
                                   'Previous photos links\n'
                                   'and photo attachment',
                    [[Buttons.screen_confirm, Buttons.screen_reject],
                     [Buttons.to_main]]
                )
            },

            {
                'condition': lambda event: self.check_payload(event, Buttons.admin_stats),
                'privilege': lambda vk, event: vk.send(
                    event.user_id, 'Кол-во проверенных скринов: 0\n'
                                   'Кол-во непроверенных скринов: 0\n'
                                   'Кол-во отвергнутых скринов: 0\n'
                                   'Кол-во непроверенных приколов: 0\n' +
                                   ''.join([f'{i+1}. ФИО vk link: 0\n' for i in range(10)])
                )
            },

            {
                'condition': lambda event: self.check_payload(event, Buttons.jokes_check),
                'privilege': lambda vk, event: vk.send(
                    event.user_id,
                    'Ты можешь добавить или отнять баллы за шутку, учитывай, что 1 скрин - 1 балл.\n'
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
                'condition': lambda event: self.check_payload(event, Buttons.jokes_next),
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
                'condition': lambda event: self.check_payload(event, Buttons.jokes_good),
                'privilege': lambda vk, event: vk.send(event.user_id, 'Сколько добавить?(Доделать)', [
                    [Buttons.change_command(Buttons.to_main, Buttons.jokes_next)]])
            },
            {
                'condition': lambda event: self.check_payload(event, Buttons.jokes_cringe),
                'privilege': lambda vk, event: vk.send(event.user_id, 'Сколько отнять?(Доделать)', [
                    [Buttons.change_command(Buttons.to_main, Buttons.jokes_next)]])
            },

            {
                'condition': lambda event: self.check_payload(event, Buttons.action_with_user),
                'privilege': lambda vk, event: vk.send(
                    event.user_id, 'Вводи id. (Будут показываться кнопки очков и только бана или только разбана)',
                    [[Buttons.ban_user, Buttons.unban_user],
                     [Buttons.add_scores, Buttons.remove_scores],
                     [Buttons.to_main]])
            },
            {
                'condition': lambda event: self.check_payload(event, Buttons.ban_user),
                'privilege': lambda vk, event: vk.send(event.user_id, 'Забанен')
            },
            {
                'condition': lambda event: self.check_payload(event, Buttons.unban_user),
                'privilege': lambda vk, event: vk.send(event.user_id, 'Разбанен')
            },
            {
                'condition': lambda event: self.check_payload(event, Buttons.add_scores),
                'privilege': lambda vk, event: vk.send(
                    event.user_id, 'Вводи кол-во очков (Доделать)',
                    [[Buttons.change_command(Buttons.to_main, Buttons.action_with_user)]])
            },
            {
                'condition': lambda event: self.check_payload(event, Buttons.remove_scores),
                'privilege': lambda vk, event: vk.send(
                    event.user_id, 'Вводи кол-во очков (Доделать)',
                    [[Buttons.change_command(Buttons.to_main, Buttons.action_with_user)]])
            },
        ]
        user_routes = [

        ]

        self.rules = [
            *button_base_rules,
            *admin_routes,
            *user_routes,

            *base_rules
        ]

    @staticmethod
    def default_action(vk, event):
        vk.send(event.user_id, 'что ты несешь-то вообще?')

    @staticmethod
    def write_log(vk, event, e):
        request_params = [param for param in e.error["request_params"] if param['key'] not in ['message', 'keyboard', 'user_id']]
        request_params.append({'keyboard': json.loads(next(iter([param for param in e.error["request_params"] if param['key'] == 'keyboard']), None)['value'])})
        msg = f'{e.error["error_code"]}: {e.error["error_msg"]}\n{json.dumps(request_params, indent=2, ensure_ascii=False)}'
        vk.send(Config.log_receiver, msg, forward_messages=event.message_id)

    @staticmethod
    def check_payload(event, key):
        if type(key) is dict:  # is button
            key = Buttons.get_key(key)
        return hasattr(event, 'payload') and literal_eval(event.payload).get('command') == key
