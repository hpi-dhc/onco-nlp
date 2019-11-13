class TNMClassification:
    
    __keyset = ['T', 'N', 'M', 'L', 'V', 'Pn', 'SX', 'R', 'G']

    def __init__(self):
        self.values = {}
        for key in self.__keyset:
            setattr(self, key, None)

    def hasvalue(self, key):
        self.__checkkey(key)
        return key in self.values

    def setvalue(self, key, value):
        self.__checkkey(key)
        if key in self.values and not value.contains(self.values[key]):
            raise Exception('Property %s can only be written once' % key)
        self.values[key] = value
        setattr(self, key, value)

    def __checkkey(self, key):
        if not key in self.__keyset:
            raise Exception('Invalid key %s' % key)

    def empty(self):
        return len(self.values) == 0

    def __repr__(self):
        res = [ ('%s: %s' % (key, self.values[key])) for key in self.__keyset if self.hasvalue(key)]
        return 'TNM(%s)' % ', '.join(res)

from onconlp.match import Match

class TNMMatch(Match):
    def __init__(self, span, prefix, value, details):
        super(TNMMatch, self).__init__(span, value)
        self.prefix = prefix
        self.details = details

    def __repr__(self):
        return 'TNM-Match (%s | %s | %s, %d, %d)' % \
            (self.prefix, self.value, self.details, self.start, self.end)

from onconlp.classification import rulebased_tnm

class TNMExtractor:

    def __init__(self, language='de', allow_spaces=False):
        self._impl = rulebased_tnm.RuleTNMExtractor(language, allow_spaces)

    def transform(self, text):
        return self._impl.transform(text)