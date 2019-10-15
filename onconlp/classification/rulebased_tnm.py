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
        'R' : r"R[0-2][ab]?",
        'G' : r"G[1-4]"
    }

    def __init__(self, language):
        self.nlp = spacy.load(language)
        rules = self.nlp.Defaults.tokenizer_exceptions
        prefixes = list(self.nlp.Defaults.prefixes)
        prefixes.extend(self.__tnm_rules.values())

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
       
        for k, v in self.__tnm_rules.items():
            self.matcher.add(k, None, [
                {"TEXT": {"REGEX" : v}}
            ])
            self.matcher.add(k, None, [
                {"TEXT": {"REGEX" : v}},
                {"TEXT": '(' },
                {"TEXT": {"REGEX" : r'[^\(\)]*'}, "OP": "+"},
                {"TEXT": ')' }
            ])
       
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
            if tnmcomponent is 'N':
                details, value = self.get_details_n(value)
            else:
                details, value = self.get_details(value)
            if tnmcomponent in ['T', 'N', 'M'] and \
                prefixes:
                cur_result.setvalue(tnmcomponent, Match(span, prefixes, value, details))
            else:
                cur_result.setvalue(tnmcomponent, Match(span, None, value, details))
        if not cur_result.empty():
            results.append(cur_result)
        return results
    
    __lymphnode_pattern = r'(\d+) ?\/ ?(\d+)'

    def get_details(self, value, details={}):
        # Any expression within braces
        match = re.search(r'\((.*)\)', value)
        if match:
            other = match.group(1).strip()
            if other:            
                details['other'] = other
            value = value[0:match.start()].strip()
        return details, value

    def get_details_n(self, value, details={}):
        match = re.search(self.__lymphnode_pattern, value)
        if match:
            details['lymphnodes_affected'] = match.group(1)
            details['lymphnodes_examined'] = match.group(2)
            value = value[:match.start()] + value[match.end():]
        # Any expression within braces
        return self.get_details(value, details)