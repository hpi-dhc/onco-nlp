import spacy
from spacy.matcher import Matcher
from spacy.tokenizer import Tokenizer
from onconlp.spacy_util import load_spacy
from onconlp.match import Match
import regex as re


class RuleICD_O_Extractor():
    
    def __init__(self, language):
        self.nlp = load_spacy(language)

        custom_infixes = ['/']
        all_prefixes_re = spacy.util.compile_prefix_regex(tuple(list(self.nlp.Defaults.prefixes) + custom_infixes))

        infix_re = spacy.util.compile_infix_regex(tuple(list(self.nlp.Defaults.infixes) + custom_infixes))

        suffix_re = spacy.util.compile_suffix_regex(tuple(list(self.nlp.Defaults.suffixes) + custom_infixes))   

        self.nlp.tokenizer = Tokenizer(self.nlp.vocab, self.nlp.Defaults.tokenizer_exceptions,
                        prefix_search = all_prefixes_re.search, 
                        infix_finditer = infix_re.finditer, 
                        suffix_search = suffix_re.search,
                        token_match=None)
        
        self.matcher = Matcher(self.nlp.vocab)

        self.matcher.add('morphology', None, [
             {"TEXT": {"REGEX" : r'\d\d\d\d'}},
             {"TEXT": {"REGEX" : r'\s'}, "OP" : "*"},
             {"TEXT": '/'},
             {"TEXT": {"REGEX" : r'\s'}, "OP" : "*"},
             {"TEXT": {"REGEX" : r'\d'}},
        ])
        

    def transform(self, text):
        morphology = []
        doc = self.nlp(text)        
        matches = self.matcher(doc)
        for match_id, start, end in matches:
            span = doc[start:end]  # The matched span
            match_type = self.nlp.vocab[match_id].text
            assert match_type == 'morphology' # Only one type right now
            morphology.append(Match(span, re.sub(r'\s', '', span.text)))
        if morphology:
            return {'icd-o' : {
                'morphology' : morphology
            }}
        else:
            return {}