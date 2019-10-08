class TNM:
    T = None
    N = None
    M = None

from onconlp.classification import rulebased_tnm

class TNMExtractor:

    def __init__(self, language='de'):
        self._impl = rulebased_tnm.RuleTNMExtractor(language)

    def process_document(self, text, split_sentences=True):
        return self._impl.process_document(text, split_sentences)