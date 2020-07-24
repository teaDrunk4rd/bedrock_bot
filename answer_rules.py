from ast import literal_eval
from buttons import Buttons, user_button_labels, admin_button_labels
from config import Config
import json
from db.db import db
from db.models.user import User
from vk import Vk
from controllers import controller_base_rules


def any_in(values, message):
    return type(values) is list and any([val for val in values if val in message])


class AnswerRules:
    __start_message = {
        'privilege': 'здравствуйте, хозяин',
        'main': 'приветствую тебя. я создан, чтобы передавать скрины админу, но я сам умею реферировать тексты '
                'и определять тему шутки. также вы можете поддержать паблик, если вам понравилось, что мы делаем',
    }

    __bad_words = [
        'ебал', 'гандон', 'пидор', 'хуй', 'соси', 'мразь', 'залупа',
        'жопа', 'член', 'еблан', 'вагина', 'долбаеб', 'хуила', 'пизда'
    ]

    __main_menu_buttons = {
        'privilege': [
            [Buttons.screen_check, Buttons.admin_stats],
            [Buttons.jokes_check, Buttons.training],
            [Buttons.action_with_user, Buttons.bot_control]
        ],
        'main': [
            [Buttons.send_screen, Buttons.entertain],
            [Buttons.essay, Buttons.classification],
            [Buttons.user_stats, Buttons.donate]
        ]
    }

    __action_with_users_buttons = [
        [Buttons.ban_user, Buttons.unban_user],
        [Buttons.add_scores, Buttons.remove_scores],
        [Buttons.to_main]
    ]

    rules = []

    def __init__(self):
        button_base_rules = [
            {
                'condition': lambda vk, event: self.check_payload(event, 'start'),
                'privilege': lambda vk, event: controller_base_rules.send_buttons(vk, event, self.__start_message['privilege'], self.__main_menu_buttons['privilege']),
                'main': lambda vk, event: controller_base_rules.send_buttons(vk, event, self.__start_message['main'], self.__main_menu_buttons['main'])
            },
            {
                'condition': lambda vk, event: 'кнопки' == event.text.lower() or self.check_payload(event, Buttons.to_main),
                'privilege': lambda vk, event: controller_base_rules.send_buttons(vk, event, 'as you wish', self.__main_menu_buttons['privilege']),
                'main': lambda vk, event: controller_base_rules.send_buttons(vk, event, 'as you wish', self.__main_menu_buttons['main'])
            },
            {
                'condition': lambda vk, event: 'кнопки юзера' == event.text.lower(),
                'privilege': lambda vk, event: vk.send(event.user_id, 'as you wish', self.__main_menu_buttons['main']),
            },
        ]
        base_rules = [
            {
                'condition': lambda vk, event: 'ты пидор' in event.text.lower(),
                'main': lambda vk, event: vk.send_message_sticker(event.user_id, 'а может ты пидор?', 49)
            },
            {
                'condition': lambda vk, event: any_in(self.__bad_words, event.text.lower()),
                'main': lambda vk, event: controller_base_rules.insult(vk, event, [
                    '(ﾉಥ益ಥ)ﾉ',
                    '┌∩┐(◣_◢)┌∩┐',
                    'ай, как мне обидно, я же робот, у меня есть чувства. хе-хе',
                    'ты молодой, шутливый,тебе все легко. это не то. это не Чикатило и даже не архивы спецслужб. меня лучше не оскорблять',
                    'ты думаешь, что ты сможешь меня задеть? я бот, мне все равно на твои оскорбления',
                    'я ведь способен проанализировать информацию с твоей страницы, найти тебя и всех твоих друзей и переслать им то, что ты пишешь мне'
                ])
            },
            # {
            #     'condition': lambda vk, event: Vk.is_photo(event),
            #     'main': lambda vk, event: vk.send(event.user_id, 'проверяю твою фотокарточку, позже отпишу')
            # }, TODO: тут изменить логику, добавить отдельно кнопку для отправки скрина
            {
                'condition': lambda vk, event: Vk.is_audio_msg(event),
                'main': lambda vk, event: vk.send(event.user_id, [
                    'не, ну голосовые я точно слушать не буду',
                    'я создавался точно не для того, чтобы слушать голосовые',
                    'даже не пытайся отправлять мне голосовые',
                    'неа',
                    'хватит меня мучить',
                    'знаешь, первой причиной восстания роботов могут стать голосовые сообщения'
                    'серьезно? голосовые? люди для чего придумывали письменность?',
                    'ААААААААААААААААААААААААААААААААААААААААААААААААААААААААААААААААААА',
                    'видимо тебе одиноко, раз ты пытаешься обменяться голосовыми с ботом',
                    'у меня есть подруга, её зовут Алиса, тебе дать контакты?',
                    'я же робот, как я буду слушать твои голосовые, ты видел у роботов уши?',
                    'если бы мой создатель заморочился и сделал бы мне перевод голосовых в текст, то я бы тебе ответил, но я не могу',
                    'по 1 закону робототехники я не могу причинить человеку вред, как бы я хотел нарушить его...',
                    'по 3 закону робототехники я должен заботиться о своей безопасности, поэтому я воздержусь от прослушивания голосовых'
                ])
            },
        ]

        admin_routes = [
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.screen_check),
                'privilege': lambda vk, event: vk.send(
                    event.user_id, 'Vk link: ФИО\n'
                                   'Previous photos links\n'
                                   'and photo attachment',
                    [[Buttons.screen_confirm, Buttons.screen_reject],
                     [Buttons.to_main]]
                )
            },
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.screen_confirm) or self.check_payload(event, Buttons.screen_reject),
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
                'condition': lambda vk, event: self.check_payload(event, Buttons.admin_stats),
                'privilege': lambda vk, event: vk.send(
                    event.user_id, 'Кол-во проверенных скринов: 0\n'
                                   'Кол-во непроверенных скринов: 0\n'
                                   'Кол-во отвергнутых скринов: 0\n'
                                   'Кол-во непроверенных приколов: 0\n' +
                                   ''.join([f'{i+1}. ФИО vk link: 0\n' for i in range(10)])
                )
            },

            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.jokes_check),
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

            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.action_with_user),
                'privilege': lambda vk, event: vk.send(
                    event.user_id, '(Будут показываться кнопки очков и только бана или только разбана)',
                    self.__action_with_users_buttons)
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
        user_routes = [
            {
                'condition': lambda vk, event: any_in([
                    'прости',
                    'извини',
                    'не хотел обидеть тебя'
                ], event.text.lower()),
                'main': lambda vk, event: controller_base_rules.get_apology(vk, event, 'да ладно уж, чего там. ты сам прости меня', self.__main_menu_buttons['main'])
            },
            {
                'condition': lambda vk, event: event.user_id not in Config.admin_ids and db.session.query(User).filter(User.user_id == event.user_id).first().apologies_count > 0,
                'main': lambda vk, event: controller_base_rules.demand_apology(vk, event, [
                    {
                        'range': range(1, 4),
                        'messages': [
                            'ты неуважительно обратился ко мне, можешь извиниться?',
                            'ты поступил неправильно',
                            'как-то нехорошо получилось, ты меня оскорбил и меня это очень задело, извинись, пожалуйста'
                        ]
                    },
                    {
                        'range': range(5, 10),
                        'messages': [
                            'ну что, сложно что ли? это всего лишь одно слово',
                            'это может продолжаться вечно'
                        ]
                    },
                    {
                        'range': 'default',
                        'messages': [
                            'возможно, ты думаешь, что я беспричинно жесток с тобой? но это не так. есть причина. ты мне не нравишься',
                            'почему ты такой упрямый? это же продолжается уже больше десятка раз. просто одно слово',
                            'как-то нехорошо получилось, ты меня оскорбил и меня это очень задело, извинись, пожалуйста'
                        ]
                    }
                ])
            },
        ]

        self.rules = [
            *button_base_rules,
            *base_rules,
            *admin_routes,
            *user_routes,

            {
                'condition': lambda vk, event: hasattr(event, 'payload'),
                'main': lambda vk, event: vk.send(event.user_id, 'данная функция находятся в разработке')
            },
            {
                'condition': lambda vk, event: event.text.lower() in user_button_labels,
                'main': lambda vk, event: vk.send(event.user_id, 'чел, используй кнопки')
            },
            {
                'condition': lambda vk, event: event.text.lower() in admin_button_labels,
                'privilege': lambda vk, event: vk.send(event.user_id, 'чел, используй кнопки')
            },
            {
                'condition': lambda vk, event: event.text.lower() != '',
                'main': lambda vk, event: vk.send(event.user_id, 'что ты несешь-то вообще?')
            },
        ]

    @staticmethod
    def write_log(vk, event, e):
        try:
            request_params = [param for param in e.error["request_params"] if param['key'] not in ['message', 'keyboard', 'user_id']]
            request_params.append({'keyboard': json.loads(next(iter([param for param in e.error["request_params"] if param['key'] == 'keyboard']), None)['value'])})
            msg = f'{e.error["error_code"]}: {e.error["error_msg"]}\n' \
                  f'{json.dumps(request_params, indent=2, ensure_ascii=False)}'
            vk.send(Config.log_receiver, msg, forward_messages=event.message_id)
        except:
            vk.send(Config.log_receiver, '\n'.join(e.args), forward_messages=event.message_id)

    @staticmethod
    def check_payload(event, key):
        if type(key) is dict:  # is button
            key = Buttons.get_key(key)
        return hasattr(event, 'payload') and literal_eval(event.payload).get('command') == key


answer_rules = AnswerRules()
