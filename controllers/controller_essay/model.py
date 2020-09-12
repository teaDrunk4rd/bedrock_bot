import gensim
from gensim.utils import simple_preprocess


class Model:
    value = []
    __freq_dict = {}
    __corpus = []

    def __init__(self, document):
        self.__freq_dict = gensim.corpora.Dictionary([simple_preprocess(document)])
        self.__corpus = self.__freq_dict.doc2bow(simple_preprocess(document))
        self.value = self.get_tf_model()

    def get_tf_model(self):
        return [
            {
                'value': self.__freq_dict[idx],
                'freq': freq,
            } for idx, freq in self.__corpus
        ]
