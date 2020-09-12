
class WordClass:
    major = 'ГОС'
    minor = 'ВОС'
    trash = 'Н'

    @staticmethod
    def get_word_class(value, words_len, paragraph_len):
        if 9 / (words_len * paragraph_len) <= value < 1:
            return WordClass.major
        if ((2 * paragraph_len / 4) ** 2) / (words_len * paragraph_len) <= value < 9 / (words_len * paragraph_len):
            return WordClass.minor
        return WordClass.trash
