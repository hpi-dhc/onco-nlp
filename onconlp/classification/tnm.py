class TNMClassification:
    T  = None
    N  = None
    M  = None
    L  = None
    V  = None
    Pn = None
    SX = None
    R = None
    G = None

    def hasvalue(self, key):
        return False

    def setvalue(self, key, value):
        pass

class Match(object):
    def __init__(self, span, value, prefix):
        self.token = span.text
        self.value = value
        self.prefix = prefix
        self.start = span[0].idx
        self.end = span[0].idx + len(span.text)
    
    def __repr__(self):
        return 'Match (%s, %d, %d)' % (self.token, self.start, self.end)

from onconlp.classification import rulebased_tnm

class TNMExtractor:

    def __init__(self, language='de'):
        self._impl = rulebased_tnm.RuleTNMExtractor(language)

    def transform(self, text):
        return self._impl.transform(text)