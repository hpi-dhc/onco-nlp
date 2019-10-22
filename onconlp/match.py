class Match():
    def __init__(self, span, value):
        self.token = span.text
        self.value = value
        self.start = span[0].idx
        self.end = span[0].idx + len(span.text)
    
    def contains(self, other):
        return self.start <= other.start and self.end >= other.end

    def __repr__(self):
        return 'Match (%s, %d, %d)' % \
            (self.value, self.start, self.end) 