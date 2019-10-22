from onconlp.diagnosis import rulebased_icd_o

class ICD_O_Extractor:

    def __init__(self, language='de'):
        self._impl = rulebased_icd_o.RuleICD_O_Extractor(language)

    def transform(self, text):
        return self._impl.transform(text)