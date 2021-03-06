import json
import os
import re
import pymorphy2
import time
from buttons import Buttons
from config import Config
from controllers.controller import Controller
from controllers.controller_essay.model import Model
from controllers.controller_essay.normalized_document import NormalizedDocument
from controllers.controller_essay.word_class import WordClass
from db.db import DB
from db.models.essay import Essay
from db.models.settings import Settings
from db.models.user import User
from multiprocessing.dummy import Pool as ThreadPool, Process

location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


class ControllerEssay(Controller):
    def __init__(self):
        super().__init__()

        self.handlers = [
            {
                'condition': lambda vk, event, user:
                    self.check_payload(event, Buttons.essay) and self.check_access(Settings.essay, event.user_id),
                'main': lambda vk, event, user: self.get_essay_button(vk, event, user)
            },
            {
                'condition': lambda vk, event, user: user.compare_path(Buttons.essay),
                'main': lambda vk, event, user: self.write_text(vk, event, user)
            },
            {
                'condition': lambda vk, event, user: self.any_in([
                    'fast test',
                    'fast_test',
                ], event.text.lower()) and self.need_process_message(user),
                'admin': lambda vk, event, user: self.fast_test_speed(vk, event, user)
            },
            {
                'condition': lambda vk, event, user: self.any_in([
                    'full test',
                    'full_test',
                ], event.text.lower()) and self.need_process_message(user),
                'admin': lambda vk, event, user: self.full_test_speed(vk, event, user)
            }
        ]
        self.morph = pymorphy2.MorphAnalyzer()
        self.calculating = False

    reject_message = 'знаешь, у меня так много текстов, я еще не прочел твой предыдущий. давай я его сначала прочту, потом отправишь новый.'

    def get_essay_button(self, vk, event, user):
        if self.db.session.query(Essay).filter(Essay.user_id == event.user_id, Essay.processed_text == None).first():
            vk.send(event.user_id, self.reject_message)
        else:
            self.db.update(user, {User.path: Buttons.get_key(Buttons.essay)})
            vk.send(event.user_id, 'давай свой текст, прочту его за тебя и в кратце расскажу в чем суть', [[Buttons.to_main]])

    def write_text(self, vk, event, user):
        if self.db.session.query(Essay).filter(Essay.user_id == event.user_id, Essay.processed_text == None).first():
            vk.send(event.user_id, self.reject_message, self.main_menu_buttons['main'])
        else:
            sentences_len = len(re.split(r'[.!?]+', event.text.replace('\n', '')))
            if sentences_len < 10:
                vk.send(event.user_id, 'чел, тут предложений не так много, давай как-нибудь сам', self.main_menu_buttons['main'])
            else:
                self.db.add(Essay(event.user_id, event.message_id, event.text))
                vk.send(event.user_id, 'мне нужно время на прочтение. я тебе обязательно напишу по поводу текста',
                        self.main_menu_buttons['main'])
                if not self.calculating:
                    p = Process(target=self.proceed_essays, args=(vk,))
                    p.start()
        self.db.update(user, {User.path: ''})

    def proceed_essays(self, vk, pool_capacity=4, is_test=False):  # run only through Process other than tests
        self.calculating = True
        while any(self.db.session.query(Essay).filter(Essay.processed_text == None)):
            essays = self.db.session.query(Essay).filter(Essay.processed_text == None).order_by(Essay.id).all()
            pool = ThreadPool(pool_capacity)  # Необходимо поэкспериментировать с кол-вом потоков на железе сервера (макс. 4)
            pool.starmap(self.generate_essay, [(vk, essay, is_test) for essay in essays])
            pool.close()
            pool.join()
        self.calculating = False

    def generate_essay(self, vk, unprocessed_essay, is_test):  # run only through Pool starmap/map
        new_db_session = DB()
        unprocessed_essay = new_db_session.session.query(Essay).get(unprocessed_essay.id)
        unprocessed_essay.processed_text = self.get_essay(unprocessed_essay.text)
        if not is_test:
            vk.send(
                unprocessed_essay.user_id,
                f'я закончил читать, вот что я могу сказать:\n{unprocessed_essay.processed_text}',
                forward_messages=unprocessed_essay.message_id
            )
        new_db_session.session.commit()
        del new_db_session

    def get_essay(self, text):
        document = NormalizedDocument(text)
        words_model = Model(document.words).value

        paragraphs = [paragraph for paragraph in text.split('\r\n') if paragraph != '']
        paragraphs_words = [Model(NormalizedDocument(paragraph).words).value for paragraph in paragraphs]

        for word in words_model:
            paragraph_words_count = len([paragraph for paragraph in paragraphs_words if
                                         any(token['value'] == word['value'] for token in paragraph)])
            k = paragraph_words_count * word['freq'] / (len(words_model) * len(paragraphs))
            word['class'] = WordClass.get_word_class(k, len(words_model), len(paragraphs))
        main_words = [word['value'] for word in words_model if word['class'] != WordClass.trash]

        stop_pairs = ['как правило', 'говорят', 'сказал', 'отмечают']
        all_sentences = []
        for paragraph in paragraphs:
            sentences = re.split(r'[.!?]+', paragraph.replace('\n', ''))
            for sentence in sentences:
                if len(sentence) in [0, 1, 2] or any(sentence in stop_word for stop_word in stop_pairs):
                    continue
                pairs = [word for word in sentence.split(' ') if self.morph.parse(word)[0].normal_form in main_words]
                all_sentences.append({
                    'sentence': sentence,
                    'power': len(pairs) / len(sentence.split(' '))
                })

        if len(all_sentences) > 3:
            all_sentences = sorted(all_sentences, key=lambda x: -x['power'])[:3]
        return '. '.join([sentence['sentence'] for sentence in all_sentences])

    def __add_for_test(self, vk):
        vk.send(Config.developer, 'okay then, give me some time')
        with open(os.path.join(location, 'test.txt'), 'r', encoding='utf-8') as f:
            return f.read().split('\n\n')

    def __delete_for_test(self, vk, texts, message):
        self.db.session.execute(Essay.__table__.delete().where(Essay.text.in_(texts)))
        self.db.session.commit()
        vk.send(Config.developer, message)

    def fast_test_speed(self, vk, event, user):
        texts = self.__add_for_test(vk)
        self.db.add([Essay(Config.developer, event.message_id, text) for text in texts])
        try:
            pool_capacity = int(event.text.replace('fast test ', '').replace('fast_test ', ''))
        except:
            pool_capacity = 4

        time_to_proceed = time.time()
        self.proceed_essays(vk, pool_capacity=pool_capacity, is_test=True)
        time_to_proceed = round(time.time() - time_to_proceed, 2)

        self.__delete_for_test(vk, texts, f'time_to_proceed({pool_capacity} thr): {time_to_proceed}')

    def full_test_speed(self, vk, event, user):
        texts = self.__add_for_test(vk)

        times = []
        for pool_capacity in range(1, 15):  # сервер падает при 5 потоках из-за нехватки памяти в 512Мб ¯\_(ツ)_/¯
            average_time = {'pool_capacity': pool_capacity}
            attempt = 5
            for i in range(attempt):
                self.db.add([Essay(Config.developer, event.message_id, text) for text in texts])
                time_to_proceed = time.time()
                self.proceed_essays(vk, pool_capacity=pool_capacity, is_test=True)
                time_to_proceed = round(time.time() - time_to_proceed, 2)
                average_time.update({i: time_to_proceed})
            times.append({
                'pool_capacity': average_time['pool_capacity'],
                'time': sum(average_time[i] for i in range(attempt)) / attempt
            })

        self.__delete_for_test(vk, texts, json.dumps(times, indent=2, ensure_ascii=False))
