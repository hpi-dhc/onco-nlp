class TNMClassification:
    
    __keyset = ['T', 'N', 'M', 'L', 'V', 'Pn', 'SX', 'R', 'G']

    def __init__(self):
        self.values = {}
        self.merged = False
        for key in self.__keyset:
            setattr(self, key, None)

    def hasvalue(self, key):
        self.__checkkey(key)
        return key in self.values

    def setvalue(self, key, value):
        self.__checkkey(key)
        if key in self.values and not value.contains(self.values[key]):
            raise Exception('Property %s can only be written once' % key)
        if not value:
            return
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

    def merge(self, other_classification):
        merged = TNMClassification()
        merged.merged = True
        for k in self.__keyset:
            if not self.hasvalue(k):
                merged.setvalue(k, getattr(other_classification, k))
            elif not other_classification.hasvalue(k):
                merged.setvalue(k, getattr(self, k))
            else:
                m = getattr(self, k).merge(getattr(other_classification, k))
                if not m:
                    return None #mismatch
                merged.setvalue(k, m)
        return merged

from onconlp.match import Match

class TNMMatch(Match):
    def __init__(self, span, prefix, value, details):
        super(TNMMatch, self).__init__(span, value)
        self.prefix = prefix
        self.details = details

    def __repr__(self):
        return 'TNM-Match (%s | %s | %s, %d, %d)' % \
            (self.prefix, self.value, self.details, self.start, self.end)

    def merge(self, other):
        if other is None:
            return self
        else:
            if self.value != other.value:
                return None
            if self.prefix and other.prefix and self.prefix != other.prefix:
                return None
            if self.details and other.details and self.details != other.details:
                return None
            if self.prefix:
                return self
            else:
                return other

from onconlp.classification import rulebased_tnm

class TNMExtractor:

    def __init__(self, language='de', allow_spaces=False, merge_matches=False, detect_parantheses=True):
        """Creates the TNM extractor
        
        Keyword Arguments:
            language {str} -- Language String (important for tokenization) (default: {'de'})
            allow_spaces {bool} -- Are spaces inbetween allowed? Example: 'T 1' instead of 'T1' (default: {False})
            merge_matches {bool} -- Will multiple matches within the same string be merged, if possible without conflict? (default: {False})
            detect_parantheses {bool} -- Will parantheses after TNM parts be detected and analyzed? Example: N1 (2/3) (default: {True})
        """
        self._impl = rulebased_tnm.RuleTNMExtractor(language, allow_spaces, merge_matches, detect_parantheses)

    def transform(self, text):
        return self._impl.transform(text)