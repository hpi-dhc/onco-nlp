from onconlp.classification.tnm import TNMClassification, Match
from onconlp.spacy_util import load_spacy
import spacy
from spacy.matcher import Matcher
from spacy.tokenizer import Tokenizer
import regex as re
import sys

class RuleTNMExtractor():

    __tnm_rules = {
        'T' : r"[yr]?[ry]?[pc]?T([0-4][a-d]?|is|a|X)",
        'N' : r"[yr]?[ry]?[pc]?N([0-3][a-d]?|X)",
        'M' : r"[yr]?[ry]?[pc]?M([0-1][a-b]?|X)",
        'L' : r"[pc]?L[0-1X]",
        'V' : r"[pc]?V[0-2X]",
        'Pn': r"[pc]?Pn[0-1X]",
        'SX': r"[pc]?SX[0-3X]",
        'R' : r"[pc]?R[0-2][ab]?",
        'G' : r"G[1-4X]"
    }

    def __init__(self, language):
        self.nlp = load_spacy(language)
        rules = self.nlp.Defaults.tokenizer_exceptions
        
        infixes = list(self.nlp.Defaults.infixes)
        infixes.append(r'[\(\)-]')
        infixes = spacy.util.compile_infix_regex(tuple(infixes)).finditer

        prefixes = list(self.nlp.Defaults.prefixes)
        prefixes.extend(list(self.__tnm_rules.values()))
        prefixes.append(r'[-/"§\$&\\]')
        prefixes = spacy.util.compile_prefix_regex(tuple(prefixes)).search

        suffixes = list(self.nlp.Defaults.suffixes)
        suffixes = spacy.util.compile_suffix_regex(tuple(suffixes)).search

        self.nlp.tokenizer = Tokenizer(self.nlp.vocab, 
                                       rules=rules,
                                       prefix_search=prefixes,
                                       suffix_search=suffixes,
                                       infix_finditer=infixes
                                       )

        self.matcher = Matcher(self.nlp.vocab)
        
        def add_rule(k, v):
            self.matcher.add(k, None, [
                {"TEXT": {"REGEX" : '(?<![A-Za-z0-9])' + v}}
            ])
            self.matcher.add(k, None, [
                {"TEXT": {"REGEX" : '(?<![A-Za-z0-9])' + v}},
                {"TEXT": {"REGEX" : r'\s'}, "OP" : "*"},
                {"TEXT": '(' },
                {"TEXT": {"REGEX" : r'[^\(\)]'}, "OP": "+"},
                {"TEXT": ')' }
            ])

        for k, v in self.__tnm_rules.items():
            add_rule(k, v)

        # Special cases
        self.add_special_cases()

    def add_special_cases(self):
        self.add_status_indicator()
        
    def add_status_indicator(self):
        def add(key, affixes):
            self.matcher.add(key, None, [
                    {"TEXT": key},
                    {"TEXT": "-"},
                    {"LOWER": "status"},
                    {"TEXT": ":", "OP" : "?"},
                    {"TEXT": {"REGEX" : affixes}}
            ])
            self.matcher.add(key, None, [
                    {"TEXT": key},
                    {"TEXT": "-"},
                    {"LOWER": "status"},
                    {"TEXT": ":", "OP" : "?"},
                    {"TEXT": {"REGEX" : affixes}},
                    {"TEXT": {"REGEX" : r'\s'}, "OP" : "*"},
                    {"TEXT": '(' },
                    {"TEXT": {"REGEX" : r'[^\(\)]'}, "OP": "+"},
                    {"TEXT": ')' }
            ])
        add('R',  "^[0-2][ab]?")
        add('V',  "^[0-2X]")
        add('Pn', "^[0-1X]")
        add('L',  "^[0-1X]")

    def transform(self, text):
        doc = self.nlp(text)        
        matches = self.matcher(doc)
        results = []
        cur_result = TNMClassification()
        for match_id, start, end in matches:
            span = doc[start:end]  # The matched span
            tnmcomponent = self.nlp.vocab[match_id].text            
            match = re.match(r'([yr]?)([yr]?)([pc]?)(.*)', span.text)
            prefixes = []
            for i in range(1, 4):
                prefix = match.group(i)
                if prefix:
                    prefixes.append(prefix)
            value = match.group(4)
            # Component already seen, so start new TNM expression
            if cur_result.hasvalue(tnmcomponent) and \
                not Match(span, None, value, None).contains(getattr(cur_result, tnmcomponent)):
                results.append(cur_result)
                cur_result = TNMClassification()
            details = {}
            if tnmcomponent is 'N':
                details, value = self.add_details_n(value, details)
            else:
                details, value = self.add_details(value, details)
            value = self.normalize_value(value)
            cur_result.setvalue(tnmcomponent, Match(span, prefixes, value, details))
        if not cur_result.empty():
            results.append(cur_result)
        return results
    
    def normalize_value(self, value):
        m = re.match(r'(R|V|L|Pn)-Status.*(\d[ab]?)', value)
        if m:
            return m.group(1) + m.group(2)
        return value

    def add_details(self, value, details):
        # Any expression within braces
        match = re.search(r'\((.*)\)', value)
        if match:
            other = match.group(1).strip()
            if other:            
                details['other'] = other
            value = value[0:match.start()].strip()
        return details, value

    def add_details_n(self, value, details):
        match = re.search(r'(\d+) ?\/ ?(\d+),?\s*', value)
        if match:
            details['lymphnodes_affected'] = int(match.group(1))
            details['lymphnodes_examined'] = int(match.group(2))
            value = value[:match.start()] + value[match.end():]
        # Any expression within braces
        return self.add_details(value, details)