import os

import pymorphy2
location = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


class NormalizedDocument:
    words = ''
    stop_words = open(os.path.join(location, 'stop.txt'), 'r', encoding='utf-8').read().split('\n')

    def __init__(self, document):
        morph = pymorphy2.MorphAnalyzer()
        document = self.remove_punctuations(document)
        for word in document.split():
            parsed_word = morph.parse(word)[0]
            replace_str = parsed_word.normal_form if parsed_word.normalized.tag.POS and word not in self.stop_words else ''
            document = document.replace(f' {word} ', f' {replace_str} ')
        self.words = document

    @staticmethod
    def remove_punctuations(document, old_values=None):
        if old_values is None:
            old_values = ['.', ',', ':', ';', '\'', '"', '«', '»', '—', '–', '-', '[', ']', '(', ')', '?', '•', '|', '+', '=', '*']
        for word in old_values:
            document = document.replace(word, ' ')
        return document
