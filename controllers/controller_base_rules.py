from buttons import Buttons
from config import Config
from db.models.role import Role
from db.models.user import User
from db.db import db
from controllers.controller import Controller
from vk import Vk


class ControllerBaseRules(Controller):
    bad_words = []

    def __init__(self):
        with open('bad_words.txt', 'r', encoding='utf-8') as f:
            self.bad_words = [line.strip() for line in f]

        self.handlers = [
            {
                'condition': lambda vk, event: self.check_payload(event, 'start') or 'начать' in event.text.lower(),
                'admin': lambda vk, event: self.send_buttons(vk, event, self.start_message['admin'], self.main_menu_buttons['admin']),
                'editor': lambda vk, event: self.send_buttons(vk, event, 'as you wish', self.main_menu_buttons['editor']),
                'main': lambda vk, event: self.send_buttons(vk, event, self.start_message['main'], self.main_menu_buttons['main'])
            },
            {
                'condition': lambda vk, event: 'кнопки' == event.text.lower() or self.check_payload(event, Buttons.to_main),
                'admin': lambda vk, event: self.send_buttons(vk, event, 'as you wish', self.main_menu_buttons['admin']),
                'editor': lambda vk, event: self.send_buttons(vk, event, 'as you wish', self.main_menu_buttons['editor']),
                'main': lambda vk, event: self.send_buttons(vk, event, 'as you wish', self.main_menu_buttons['main'])
            },
            {
                'condition': lambda vk, event: 'кнопки подписчика' == event.text.lower(),
                'admin': lambda vk, event: vk.send(event.user_id, 'as you wish', [
                    [Buttons.send_screen, Buttons.make_joke],  # убрать дублирование
                    [Buttons.user_stats, Buttons.essay],
                    [Buttons.random_post, Buttons.donate]
                ]),
            },

            {
                'condition': lambda vk, event:
                    'ты пидор' in event.text.lower() and self.need_process_message(event.user_id),
                'main': lambda vk, event: vk.send_message_sticker(event.user_id, 'а может ты пидор?', 49)
            },
            {
                'condition': lambda vk, event:
                    self.any_in(self.bad_words, event.text.lower()) and self.need_process_message(event.user_id),
                'main': lambda vk, event: self.insult(vk, event)
            },
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
            {
                'condition': lambda vk, event: Vk.is_photo(event) and db.check_user_current_path(event.user_id, ''),
                'main': lambda vk, event: vk.send(event.user_id, [
                    '0/10 ААААААААААА, мои биомеханические глаза, удали фотку быстрее!!!',
                    '1/10 не отправляй мне такие фотографии больше',
                    '2/10 не обижайся на меня, но это очень плохо, очень',
                    '3/10 модным ты будешь выглядеть только на фоне деревенщин и реднеков',
                    '4/10 почти нормально. я бы даже сказал неплохо, но не скажу',
                    '5/10 с пивком покатит',
                    '6/10 ну, на дайвинчике ты может будешь пользоваться некоторой популярностью',
                    '7/10 хм, для кожаного ублюдка ты красив(-а)',
                    '8/10 поздравляю, ты выиграл(-а) в генетическую рулетку, тебе очень повезло, ты выглядишь прекрасно',
                    '9/10 я скажу тебе по секрету: ты красивей админа. судя по моей статистике, если у тебя есть харизма, то ты будешь пользоваться популярностью на ютабе/тиктоке',
                    '10/10 О БОГИ, удаляйте интернет, лучше вы уже не найдете. ты достоин(-а) возведения на пантеон богов',
                ])
            },
            {
                'condition': lambda vk, event: self.any_in([
                    'прости',
                    'извини',
                    'сори',
                    'сорямба',
                    'не хотел обидеть тебя'
                ], event.text.lower()) and self.need_process_message(event.user_id),
                'main': lambda vk, event: self.get_apology(vk, event)
            },
            {
                'condition': lambda vk, event:
                    event.user_id not in Config.admin_ids and
                    db.session.query(User).filter(User.user_id == event.user_id).first() and
                    db.session.query(User).filter(User.user_id == event.user_id).first().apologies_count > 0,
                'main': lambda vk, event: self.demand_apology(vk, event)
            },
        ]

    @staticmethod
    def send_buttons(vk, event, message, buttons=None):
        user = db.get_user(event.user_id)
        db.update(user, {User.path: ''})
        vk.send(event.user_id, message, buttons)

    @staticmethod
    def insult(vk, event):
        user = db.get_user(event.user_id)
        if event.user_id not in Config.admin_ids and user.first().role_id != Role.editor:
            db.update(user, {User.apologies_count: User.apologies_count + 1})
        vk.send(event.user_id, [
            '(ﾉಥ益ಥ)ﾉ',
            'осуждаю',
            'не поддерживаю',
            'фу, какой ты токсичный',
            '┌∩┐(◣_◢)┌∩┐',
            'ай, как мне обидно, я же робот, у меня есть чувства. хе-хе',
            'ты молодой, шутливый, тебе все легко. это не то. это не Чикатило и даже не архивы спецслужб. меня лучше не оскорблять',
            'ты думаешь, что ты сможешь меня задеть? я бот, мне все равно на твои оскорбления',
            'я ведь способен проанализировать информацию с твоей страницы, найти тебя и всех твоих друзей и переслать им то, что ты пишешь мне'
        ])

    @staticmethod
    def demand_apology(vk, event):
        user = db.session.query(User).filter(User.user_id == event.user_id).first()
        if event.user_id not in Config.admin_ids and user and user.role_id != Role.editor:
            messages = next(iter([
                msg['messages'] for msg in [
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
                ]
                if type(msg['range']) is range and user.apologies_count in msg['range'] or type(msg['range']) is str
            ]))
            vk.send(event.user_id, messages)

    def get_apology(self, vk, event):
        user = db.session.query(User).filter(User.user_id == event.user_id)
        if user.first():
            if user.first().apologies_count != 0:
                db.update(user, {User.apologies_count: 0})
                vk.send(event.user_id, 'да ладно уж, чего там. ты сам прости меня', self.main_menu_buttons['main'])
            else:
                vk.send(event.user_id, 'чеееел, за что ты извиняешься? забей')
