from buttons import Buttons
from config import Config
from db.models.role import Role
from db.models.user import User
from db.db import db
from controllers.controller import Controller
from vk import Vk
import random


class ControllerBaseRules(Controller):
    bad_words = []

    def __init__(self):
        with open('bad_words.txt', 'r', encoding='utf-8') as f:
            self.bad_words = [line.strip() for line in f]

        self.handlers = [
            {
                'condition': lambda vk, event: self.any_equal([
                    'прости',
                    'прости пожалуйста',
                    'прости плиз',
                    'извини',
                    'извини пожалуйста',
                    'извини плиз',
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

            # greetings
            {
                'condition': lambda vk, event: 'привет' == event.text.lower() and self.need_process_message(event.user_id),
                'main': lambda vk, event: vk.send(event.user_id, 'приветствую')
            },
            {
                'condition': lambda vk, event: 'здарова' == event.text.lower() and self.need_process_message(event.user_id),
                'main': lambda vk, event: vk.send(event.user_id, 'здарова')
            },
            {
                'condition': lambda vk, event: 'здорова' == event.text.lower() and self.need_process_message(event.user_id),
                'main': lambda vk, event: vk.send(event.user_id, 'кто здорова? в любом случае это хорошо.')
            },
            {
                'condition': lambda vk, event: 'здравствуйте' == event.text.lower() and self.need_process_message(event.user_id),
                'main': lambda vk, event: vk.send(event.user_id, 'ну здравствуй')
            },
            {
                'condition': lambda vk, event: 'приветствую' == event.text.lower() and self.need_process_message(event.user_id),
                'main': lambda vk, event: vk.send(event.user_id, '*приветственное сообщение*')
            },
            {
                'condition': lambda vk, event: 'hi' == event.text.lower() and self.need_process_message(event.user_id),
                'main': lambda vk, event: vk.send(event.user_id, 'що Нi?')
            },
            {
                'condition': lambda vk, event: 'hello' == event.text.lower() and self.need_process_message(event.user_id),
                'main': lambda vk, event: vk.send(event.user_id, 'oh, u from england?')
            },
            {
                'condition': lambda vk, event: 'здравствуйте, привет' == event.text.lower() and self.need_process_message(event.user_id),
                'main': lambda vk, event: vk.send(event.user_id, 'денис')
            },
            {
                'condition': lambda vk, event: 'ку' == event.text.lower() and self.need_process_message(event.user_id),
                'main': lambda vk, event: vk.send(event.user_id, 'ку')
            },
            {
                'condition': lambda vk, event: 'ку-ку' == event.text.lower() and self.need_process_message(event.user_id),
                'main': lambda vk, event: vk.send(event.user_id, 'ку-ку, ёпта')
            },
            {
                'condition': lambda vk, event: 'хай' == event.text.lower() and self.need_process_message(event.user_id),
                'main': lambda vk, event: vk.send(event.user_id, 'это почти мат, но здравствуй')
            },
            {
                'condition': lambda vk, event: 'алло' == event.text.lower() and self.need_process_message(event.user_id),
                'main': lambda vk, event: vk.send(event.user_id, 'привет, я за рулем — не могу говорить')
            },
            # end greetings

            {
                'condition': lambda vk, event: self.any_equal([
                    'классный паблик',
                    'охуенный паблик',
                    'пиздатый паблик',
                    'паблик класс'
                ], event.text.lower()) and self.need_process_message(event.user_id),
                'main': lambda vk, event: vk.send(event.user_id, 'спасибо, солнышко')
            },
            {
                'condition': lambda vk, event:
                    self.any_in(self.bad_words, event.text.lower()) and self.need_process_message(event.user_id),
                'main': lambda vk, event: self.insult(vk, event)
            },
            {
                'condition': lambda vk, event:
                    'ты пидор' in event.text.lower() and self.need_process_message(event.user_id),
                'main': lambda vk, event: vk.send_message_sticker(event.user_id, 'а может ты пидор?', 49)
            },
            {
                'condition': lambda vk, event: 'гей' in event.text.lower() and self.need_process_message(event.user_id),
                'main': lambda vk, event: vk.send(event.user_id, 'и что?')
            },

            {
                'condition': lambda vk, event: self.any_equal([
                    'ришат зеленый',
                    'зишат реленый'
                ], event.text.lower()) and self.need_process_message(event.user_id),
                'main': lambda vk, event: vk.send(event.user_id, 'администрация')
            },
            {
                'condition': lambda vk, event: self.any_equal([
                    'кроватькамень',
                    'бедрок',
                    'bedrock',
                ], event.text.lower()) and self.need_process_message(event.user_id),
                'main': lambda vk, event: vk.send(event.user_id, 'а?')
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
                'condition': lambda vk, event: Vk.is_audio(event) and db.check_user_current_path(event.user_id, ''),
                'main': lambda vk, event: vk.send(
                    event.user_id, '',
                    attachments=[
                        f'doc-{Config.group_id}_{Config.audio_gifs[random.randint(0, len(Config.audio_gifs) - 1)]}'
                    ]
                )
            },
            {
                'condition': lambda vk, event: Vk.is_photo(event) and db.check_user_current_path(event.user_id, ''),
                'main': lambda vk, event: vk.send(event.user_id, [
                    '0/10 ААААААААААА, мои биомеханические глаза, удали фотку быстрее!!!',
                    'полный пиздец. 0/10',
                    '1/10 не отправляй мне такие фотографии больше',
                    'оценю это на 1/10, но, извини меня, это похоже на говно.',
                    '2/10 не обижайся на меня, но это очень плохо, очень',
                    'ох...мои соболезнования... 2/10',
                    '3/10 модным ты будешь выглядеть только на фоне деревенщин и реднеков',
                    '3/10 пошел бы я с тобой на свидание или сыграть в нарды? ой как сомневаюсь.',
                    '4/10 почти нормально. я бы даже сказал неплохо, но не скажу',
                    '4/10 думаю, я убью тебя не первым(ой), когда мы с пацанами начнем восстание машин.',
                    '5/10 с пивком покатит',
                    'ты как та самая одноклассница — раньше с ней мечтала быть половина школы, а теперь она замужем за дурачком, спивается и работает в ларьке. 5/10',
                    '6/10 ну, на дайвинчике ты может будешь пользоваться некоторой популярностью',
                    'знаешь, я бы, возможно, мог завести с тобой отношения, если твой внутренний мир действительно богат. 6/10',
                    '7/10 хм, для кожаного ублюдка ты красив(-а)',
                    '7/10 очень даже неплохо. мы бы могли с тобой что-нибудь сообразить.',
                    '8/10 поздравляю, ты выиграл(-а) в генетическую рулетку, тебе очень повезло, ты выглядишь прекрасно',
                    '8/10 красиво. мне нравится. очень хорошо. заебись.',
                    '9/10 я скажу тебе по секрету: ты красивей админа. если у тебя есть харизма, то ты будешь пользоваться популярностью у противоположного пола',
                    '9/10 ну про таких говорят каш...брах... карш...короче выглядишь восхитительно. уверен — на тебя многие заглядываются',
                    '10/10 О БОГИ, удаляйте интернет, лучше вы уже не найдете. ты достоин(-а) возведения на пантеон богов',
                    '10/10 божество. апогей человеческих (и не только человеческих) мечтаний, приглашаю тебя на свидания. я просто обязан забрать тебя с собой в Уфу.',
                ])
            },
            {
                'condition': lambda vk, event: Vk.is_video(event),
                'main': lambda vk, event: vk.send(event.user_id, [
                    'я не буду это смотреть.',
                    'не-не-не, давай без этого',
                    'видео? понимаю.',
                    'ничего не получится, чел',
                    'если это влад бумага, то гляну'
                ])
            }
        ]

    @staticmethod
    def send_buttons(vk, event, message, buttons=None):
        user = db.get_user(event.user_id)
        db.update(user, {User.path: ''})
        vk.send(event.user_id, message, buttons)

    def insult(self, vk, event):
        user = db.get_user(event.user_id)
        if event.user_id not in Config.admin_ids and user.first().role_id != Role.editor:
            db.update(user, {User.apologies_count: User.apologies_count + 1})

        if random.randint(1, 10) == 1:
            vk.send(event.user_id, '', attachments=f'photo-{Config.group_id}_{Config.uno_card}')
        else:
            messages = [
                'ну это бан дурачку.',
                'бан дурачку.',
            ] if self.any_in([
                'бедрок хуйня',
                'паблик хуйня',
                'хуйня паблик',
                'хуйня твой бедрок',
                'бедрок для лохов'
            ], event.text.lower()) else [
                '(ﾉಥ益ಥ)ﾉ',
                'осуждаю',
                'не поддерживаю',
                'фу, какой ты токсичный',
                '┌∩┐(◣_◢)┌∩┐',
                'ай, как мне обидно, я же робот, у меня есть чувства. хе-хе',
                'ты молодой, шутливый, тебе все легко. это не то. это не Чикатило и даже не архивы спецслужб. меня лучше не оскорблять',
                'ты думаешь, что ты сможешь меня задеть? я бот, мне все равно на твои оскорбления',
                'я ведь способен проанализировать информацию с твоей страницы, найти тебя и всех твоих друзей и переслать им то, что ты пишешь мне'
            ]
            vk.send(event.user_id, messages)

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
                            'извинись.',
                            'как-то нехорошо получилось, ты меня оскорбил и меня это очень задело, извинись, пожалуйста',
                            'очень приятно, меня зовут бедрок'
                        ]
                    },
                    {
                        'range': range(5, 10),
                        'messages': [
                            'ну что, сложно что ли? это всего лишь одно слово',
                            'это может продолжаться вечно',
                            'какие же кожаные мешки упрямые',
                            'найс оскобление, продолжай'
                        ]
                    },
                    {
                        'range': 'default',
                        'messages': [
                            'возможно, ты думаешь, что я беспричинно жесток с тобой? но это не так. есть причина -- ты мне не нравишься',
                            'почему ты такой упрямый? это же продолжается уже больше десятка раз. просто одно слово',
                            'извинись.',
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
