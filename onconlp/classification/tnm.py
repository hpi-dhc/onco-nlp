class TNM:
    T = None
    N = None
    M = None

from onconlp.classification import rulebased_tnm

class TNMExtractor:    
    def process_document(self, text):
        return rulebased_tnm.process_document(text)
        
    def process_sentence(self, text):
        return rulebased_tnm.process_sentence(text)