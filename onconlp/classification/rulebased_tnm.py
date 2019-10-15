from onconlp.classification.tnm import TNMClassification, Match
import spacy
from spacy.matcher import Matcher
from spacy.tokenizer import Tokenizer
import regex as re

class RuleTNMExtractor():

    __tnm_rules = {
        'T' : r"[yr]?[ry]?[pc]?T([0-4][ab]?|is|a|X)",
        'N' : r"[yr]?[ry]?[pc]?N([0-3]|X)",
        'M' : r"[yr]?[ry]?[pc]?M([0-1]|X)",
        'L' : r"L[0-1]",
        'V' : r"V[0-2]",
        'Pn': r"Pn[0-1]",
        'SX': r"SX[0-3X]",
        'R' : r"R[0-2]",
        'G' : r"G[1-4]"
    }

    __lymphnode_pattern = r'\( ?\d+ ?\/ ?\d+ ?\)'

    def __init__(self, language):
        self.nlp = spacy.load(language)
        rules = self.nlp.Defaults.tokenizer_exceptions
        prefixes = list(self.nlp.Defaults.prefixes)
        prefixes.extend(self.__tnm_rules.values())
        prefixes.append(self.__lymphnode_pattern)
        prefixes = spacy.util.compile_prefix_regex(tuple(prefixes)).search
        suffixes = spacy.util.compile_suffix_regex(self.nlp.Defaults.suffixes).search
        infixes = spacy.util.compile_infix_regex(self.nlp.Defaults.infixes).finditer

        self.nlp.tokenizer = Tokenizer(self.nlp.vocab, 
                                rules=rules,
                                prefix_search=prefixes,
                                suffix_search=suffixes,
                                infix_finditer=infixes)
        self.matcher = Matcher(self.nlp.vocab)
        # Special handling for lymph node details
        self.matcher.add('N', None, [
            {"TEXT": {"REGEX" : self.__tnm_rules['N']}},
            {"TEXT": {"REGEX" : self.__lymphnode_pattern}}
        ])

        for k, v in self.__tnm_rules.items():
            if (k != 'N'):
                self.matcher.add(k, None, [
                    {"TEXT": {"REGEX" : v}}
                ])
       
    def transform(self, text):
        doc = self.nlp(text)        
        matches = self.matcher(doc)
        results = []
        cur_result = TNMClassification()
        for match_id, start, end in matches:
            span = doc[start:end]  # The matched span
            tnmcomponent = self.nlp.vocab[match_id].text
            if cur_result.hasvalue(tnmcomponent):
                results.append(cur_result)
                cur_result = TNMClassification()
            m = re.match(r'([yr]?)([yr]?)([pc]?)(.*)', span.text)
            prefixes = []
            for i in range(1, 4):
                prefix = m.group(i)
                if prefix:
                    prefixes.append(prefix)
            value = m.group(4)
            if tnmcomponent in ['T', 'N', 'M'] and len(prefixes) > 0:
                cur_result.setvalue(tnmcomponent, Match(span, prefixes, value))
            else:
                cur_result.setvalue(tnmcomponent, Match(span, None, value))
        if not cur_result.empty():
            results.append(cur_result)
        return results
        