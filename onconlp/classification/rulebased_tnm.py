from onconlp.classification.tnm import TNM
import spacy
from spacy.matcher import Matcher

class RuleTNMExtractor():

    def __init__(self, language):
        self.nlp = spacy.load(language)
        self.matcher = Matcher(self.nlp.vocab)
        pattern = [{"TEXT": {"REGEX" : "T\d"}}]
        self.matcher.add("TNM_T", None, pattern)

    def process_document(self, text, split_sentences):
        doc = self.nlp(text)        
        if split_sentences:
            return [self.process(self.nlp(s.text)) for s in doc.sents]
        else:
            return self.process(doc)
            
    def process(self, text):
        matches = self.matcher(text)
        results = []
        for match_id, start, end in matches:
            string_id = self.nlp.vocab.strings[match_id]  # Get string representation
            span = text[start:end]  # The matched span
            results.append((string_id, start, end, span.text))
        return results