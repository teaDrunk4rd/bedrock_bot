from buttons import Buttons
from config import Config
from db.models.user import User
from controllers.controller import Controller
from vk import Vk
import random


class ControllerBaseRules(Controller):
    bad_words = []

    def __init__(self):
        super().__init__()

        with open('bad_words.txt', 'r', encoding='utf-8') as f:
            self.bad_words = [line.strip() for line in f]

        self.handlers = [
            {
                'condition': lambda vk, event, user: self.any_equal([
                    'прости',
                    'прости пожалуйста',
                    'прости плиз',
                    'извини',
                    'извини пожалуйста',
                    'извини плиз',
                    'сори',
                    'сорямба',
                    'не хотел обидеть тебя'
                ], event.text.lower()) and self.need_process_message(user),
                'main': lambda vk, event, user: self.get_apology(vk, event, user)
            },
            {
                'condition': lambda vk, event, user: event.user_id not in Config.admin_ids and user.apologies_count > 0,
                'main': lambda vk, event, user: self.demand_apology(vk, event, user)
            },

            {
                'condition': lambda vk, event, user:
                    self.check_payload(event, 'start') or 'начать' == event.text.lower(),
                'admin': lambda vk, event, user:
                    self.send_buttons(vk, event, user, self.start_message['admin'], self.main_menu_buttons['admin']),
                'main': lambda vk, event, user:
                    self.send_buttons(vk, event, user, self.start_message['main'], self.main_menu_buttons['main'])
            },
            {
                'condition': lambda vk, event, user:
                    'кнопки' == event.text.lower() or self.check_payload(event, Buttons.to_main),
                'admin': lambda vk, event, user:
                    self.send_buttons(vk, event, user, 'as you wish', self.main_menu_buttons['admin']),
                'main': lambda vk, event, user:
                    self.send_buttons(vk, event, user, 'as you wish', self.main_menu_buttons['main'])
            },
            {
                'condition': lambda vk, event, user: 'кнопки подписчика' == event.text.lower(),
                'admin': lambda vk, event, user: vk.send(event.user_id, 'as you wish', self.__raw_main_buttons),
            },

            # greetings
            {
                'condition': lambda vk, event, user:
                    'привет' == event.text.lower() and self.need_process_message(user),
                'main': lambda vk, event, user: vk.send(event.user_id, 'приветствую')
            },
            {
                'condition': lambda vk, event, user:
                    'здарова' == event.text.lower() and self.need_process_message(user),
                'main': lambda vk, event, user: vk.send(event.user_id, 'здарова')
            },
            {
                'condition': lambda vk, event, user:
                    'здравствуйте' == event.text.lower() and self.need_process_message(user),
                'main': lambda vk, event, user: vk.send(event.user_id, 'ну здравствуй')
            },
            {
                'condition': lambda vk, event, user:
                    'приветствую' == event.text.lower() and self.need_process_message(user),
                'main': lambda vk, event, user: vk.send(event.user_id, '*приветственное сообщение*')
            },
            {
                'condition': lambda vk, event, user:
                    'hi' == event.text.lower() and self.need_process_message(user),
                'main': lambda vk, event, user: vk.send(event.user_id, 'що Нi?')
            },
            {
                'condition': lambda vk, event, user:
                    'hello' == event.text.lower() and self.need_process_message(user),
                'main': lambda vk, event, user: vk.send(event.user_id, 'oh, u from england?')
            },
            {
                'condition': lambda vk, event, user:
                    'здравствуйте, привет' == event.text.lower() and self.need_process_message(user),
                'main': lambda vk, event, user: vk.send(event.user_id, 'привет, денис')
            },
            {
                'condition': lambda vk, event, user: 'ку' == event.text.lower() and self.need_process_message(user),
                'main': lambda vk, event, user: vk.send(event.user_id, 'ку')
            },
            {
                'condition': lambda vk, event, user: 'ку-ку' == event.text.lower() and self.need_process_message(user),
                'main': lambda vk, event, user: vk.send(event.user_id, 'ку-ку, ёпта')
            },
            {
                'condition': lambda vk, event, user: 'алло' == event.text.lower() and self.need_process_message(user),
                'main': lambda vk, event, user: vk.send(event.user_id, 'привет, я за рулем — не могу говорить')
            },
            # end greetings

            {
                'condition': lambda vk, event, user: self.any_equal([
                    'классный паблик',
                    'охуенный паблик',
                    'пиздатый паблик',
                    'паблик класс'
                ], event.text.lower()) and self.need_process_message(user),
                'main': lambda vk, event, user: vk.send(event.user_id, 'спасибо, солнышко')
            },
            {
                'condition': lambda vk, event, user:
                    self.any_in(self.bad_words, event.text.lower()) and self.need_process_message(user),
                'main': lambda vk, event, user: self.insult(vk, event, user)
            },
            {
                'condition': lambda vk, event, user:
                    'ты пидор' in event.text.lower() and self.need_process_message(user),
                'main': lambda vk, event, user: vk.send_message_sticker(event.user_id, 'а может ты пидор?', 49)
            },
            {
                'condition': lambda vk, event, user: self.any_equal([
                    'гей',
                    'ты гей'
                ], event.text.lower()) and self.need_process_message(user),
                'main': lambda vk, event, user: vk.send(event.user_id, [
                    'и что?',
                    'traps aren\'t gay',
                    'вообще-то мне нравятся гендерфлюидные вертосексуалы, идентифицирующие себя как боевой вертолет Апач, мерзкая ты хуемразь'
                ])
            },

            {
                'condition': lambda vk, event, user: self.any_equal([
                    'ришат зеленый',
                    'зишат реленый'
                ], event.text.lower()) and self.need_process_message(user),
                'main': lambda vk, event, user: vk.send(event.user_id, 'администрация')
            },
            {
                'condition': lambda vk, event, user:
                    event.text.lower() == 'ришат салихов' and self.need_process_message(user),
                'main': lambda vk, event, user: vk.send(event.user_id, 'ничего про это не знаю')
            },
            {
                'condition': lambda vk, event, user: self.any_equal([
                    'кроватькамень',
                    'бедрок',
                    'bedrock',
                ], event.text.lower()) and self.need_process_message(user),
                'main': lambda vk, event, user: vk.send(event.user_id, 'а?')
            },

            {
                'condition': lambda vk, event, user:
                    Vk.is_audio_msg(event) and user.compare_path(''),
                'main': lambda vk, event, user: vk.send(event.user_id, [
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
                'condition': lambda vk, event, user: Vk.is_audio(event) and user.compare_path(''),
                'main': lambda vk, event, user: vk.send(
                    event.user_id, '',
                    attachments=[
                        f'doc-{Config.group_id}_{Config.audio_gifs[random.randint(0, len(Config.audio_gifs) - 1)]}'
                    ]
                )
            },
            {
                'condition': lambda vk, event, user: Vk.is_photo(event) and user.compare_path(''),
                'main': lambda vk, event, user: vk.send(event.user_id, [
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
                'condition': lambda vk, event, user: Vk.is_video(event) and user.compare_path(''),
                'main': lambda vk, event, user: vk.send(event.user_id, [
                    'я не буду это смотреть.',
                    'не-не-не, давай без этого',
                    'видео? понимаю.',
                    'ничего не получится, чел',
                    'если это влад бумага, то гляну'
                ])
            }
        ]

    def send_buttons(self, vk, event, user, message, buttons):
        self.db.update(user, {User.path: ''})
        vk.send(event.user_id, message, buttons)

    def insult(self, vk, event, user):
        if event.user_id not in Config.admin_ids:
            self.db.update(user, {User.apologies_count: User.apologies_count + 1})

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
                'найс оскобление, продолжай',
                'не поддерживаю',
                'фу, какой ты токсичный',
                'очень приятно, меня зовут бедрок',
                '┌∩┐(◣_◢)┌∩┐',
                'ай, как мне обидно, я же робот, у меня есть чувства. хе-хе',
                'ты молодой, шутливый, тебе все легко. это не то. это не Чикатило и даже не архивы спецслужб. меня лучше не оскорблять',
                'ты думаешь, что ты сможешь меня задеть? я бот, мне все равно на твои оскорбления',
                'я ведь способен проанализировать информацию с твоей страницы, найти тебя и всех твоих друзей и переслать им то, что ты пишешь мне'
            ]
            vk.send(event.user_id, messages)

    @staticmethod
    def demand_apology(vk, event, user):
        if event.user_id not in Config.admin_ids:
            messages = next(iter([
                msg['messages'] for msg in [
                    {
                        'range': range(1, 4),
                        'messages': [
                            'ты неуважительно обратился ко мне, можешь извиниться?',
                            'извинись.',
                            'как-то нехорошо получилось, ты меня оскорбил и меня это очень задело, извинись, пожалуйста'
                        ]
                    },
                    {
                        'range': range(5, 10),
                        'messages': [
                            'ну что, сложно что ли? это всего лишь одно слово',
                            'это может продолжаться вечно',
                            'какие же кожаные мешки упрямые'
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

    def get_apology(self, vk, event, user):
        if user.apologies_count != 0:
            self.db.update(user, {User.apologies_count: 0})
            vk.send(event.user_id, 'да ладно уж, чего там. ты сам прости меня', self.main_menu_buttons['main'])
        else:
            vk.send(event.user_id, 'чеееел, за что ты извиняешься? забей')
