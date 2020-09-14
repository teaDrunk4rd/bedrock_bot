import re
import pymorphy2
from buttons import Buttons
from controllers.controller import Controller
from controllers.controller_essay.model import Model
from controllers.controller_essay.normalized_document import NormalizedDocument
from controllers.controller_essay.word_class import WordClass
from db.db import db
from db.models.essay import Essay
from db.models.settings import Settings
from db.models.user import User
from multiprocessing.dummy import Pool as ThreadPool, Process


class ControllerEssay(Controller):
    def __init__(self):
        self.handlers = [
            {
                'condition': lambda vk, event: self.check_payload(event, Buttons.essay) and
                                               self.check_access(Settings.essay, event.user_id),
                'main': lambda vk, event: self.get_essay_button(vk, event)
            },
            {
                'condition': lambda vk, event: db.check_user_current_path(event.user_id, Buttons.essay),
                'main': lambda vk, event: self.write_text(vk, event)
            }
        ]
        self.morph = pymorphy2.MorphAnalyzer()
        self.calculating = False

    @staticmethod
    def get_reject_message():
        return 'знаешь, у меня так много текстов, я еще не прочел твой предыдущий. давай я его сначала прочту, потом отправишь новый.'

    def get_essay_button(self, vk, event):
        user = db.get_user(event.user_id)
        if db.session.query(Essay).filter(Essay.user_id == event.user_id, Essay.processed_text == None).first():
            vk.send(event.user_id, self.get_reject_message())
        else:
            db.update(user, {User.path: Buttons.get_key(Buttons.essay)})
            vk.send(event.user_id, 'давай свой текст, прочту его за тебя и в кратце расскажу в чем суть', [[Buttons.to_main]])

    def write_text(self, vk, event):
        user = db.get_user(event.user_id)
        if db.session.query(Essay).filter(Essay.user_id == event.user_id, Essay.processed_text == None).first():
            vk.send(event.user_id, self.get_reject_message(), self.main_menu_buttons['main'])
        else:
            db.add(Essay(event.user_id, event.message_id, event.text))
            vk.send(event.user_id, 'мне нужно время на прочтение. я тебе обязательно напишу по поводу текста',
                    self.main_menu_buttons['main'])
            if not self.calculating:
                p = Process(target=self.proceed_essays, args=(vk,))
                p.start()
        db.update(user, {User.path: ''})

    def proceed_essays(self, vk):  # start only via Process
        self.calculating = True
        while any(db.session.query(Essay).filter(Essay.processed_text == None)):
            all_essays = db.session.query(Essay).filter(Essay.processed_text == None).order_by(Essay.id).all()
            pool = ThreadPool(4)  # Необходимо поэкспериментировать с кол-вом потоков на железе сервера
            pool.starmap(self.generate_essay, [(vk, essay) for essay in all_essays])
            pool.close()
            pool.join()
        self.calculating = False

    def generate_essay(self, vk, unprocessed_essay):
        unprocessed_essay.processed_text = self.get_essay(unprocessed_essay.text)
        vk.send(
            unprocessed_essay.user_id,
            f'я закончил читать, вот что я могу сказать:\n{unprocessed_essay.processed_text}',
            forward_messages=unprocessed_essay.message_id
        )
        db.session.commit()

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
            sentences = re.split(r'[.!?]+', paragraph)
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
