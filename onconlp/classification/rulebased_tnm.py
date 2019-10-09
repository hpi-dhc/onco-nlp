from onconlp.classification.tnm import TNMClassification, Match
import spacy
from spacy.matcher import Matcher
from spacy.tokenizer import Tokenizer

class RuleTNMExtractor():

    tnm_rules = {
        'T' : "[cp]?T([0-4][ab]?|is|a|X)",
        'N' : "[cp]?N([0-3]|X)",
        'M' : "[cp]?M([0-1]|X)",
        'L' : "L[0-1]",
        'V' : "V[0-2]",
        'Pn': "Pn[0-1]",
        'SX': "SX[0-3X]",
        'R' : "R[0-2]",
        'G' : "G[1-4]"
    }

    def __init__(self, language):
        self.nlp = spacy.load(language)
        rules = self.nlp.Defaults.tokenizer_exceptions
        prefixes = list(self.nlp.Defaults.prefixes)
        prefixes.extend(self.tnm_rules.values())
        prefixes = spacy.util.compile_prefix_regex(tuple(prefixes)).search
        suffixes = spacy.util.compile_suffix_regex(self.nlp.Defaults.suffixes).search
        infixes = spacy.util.compile_infix_regex(self.nlp.Defaults.infixes).finditer

        def custom_tokenizer(nlp):
            return Tokenizer(nlp.vocab, 
                            rules=rules,
                            prefix_search=prefixes,
                            suffix_search=suffixes,
                            infix_finditer=infixes)

        self.nlp.tokenizer = custom_tokenizer(self.nlp)
        self.matcher = Matcher(self.nlp.vocab)
        for k, v in self.tnm_rules.items():
            self.matcher.add(k, None, [
                {"TEXT": {"REGEX" : v}}
            ])

    def transform(self, text):
        doc = self.nlp(text)        
        return self.process(doc)
            
    def process(self, text):
        matches = self.matcher(text)
        results = []
        for match_id, start, end in matches:
            span = text[start:end]  # The matched span
            print(self.nlp.vocab[match_id])
            results.append(Match(span, None, span))
        return results