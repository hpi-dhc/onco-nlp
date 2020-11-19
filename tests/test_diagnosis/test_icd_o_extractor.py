import unittest
from onconlp.diagnosis.icd_o import ICD_O_Extractor

extractor = ICD_O_Extractor('de')

class TestICD_O_Extractor(unittest.TestCase):

    def test_morphology(self):
        result = extractor.transform('123/3')
        self.assertEqual(result, {})

    def test_morphology_1(self):
        result = extractor.transform('1234/3')
        self.assertIn('icd-o', result)
        self.assertIn('morphology', result['icd-o'])
        codes = result['icd-o']['morphology']
        self.assertEqual(len(codes), 1)
        self.assertEqual(codes[0].start, 0)
        self.assertEqual(codes[0].end, 6)
        self.assertEqual(codes[0].value, '1234/3')

    def test_morphology_spaces(self):
        for morph in ['1234 / 3', '1234/ 3', '1234 /3', '1234  /3']:
            result = extractor.transform(morph)
            self.assertIn('icd-o', result, morph)
            self.assertIn('morphology', result['icd-o'])
            codes = result['icd-o']['morphology']
            self.assertEqual(len(codes), 1)
            self.assertEqual(codes[0].start, 0)
            self.assertEqual(codes[0].end, len(morph))
            self.assertEqual(codes[0].value, '1234/3')

    def test_morphology_multiple(self):
        result = extractor.transform('1234/3, 6789/8')
        self.assertIn('icd-o', result)
        self.assertIn('morphology', result['icd-o'])
        codes = result['icd-o']['morphology']
        self.assertEqual(len(codes), 2)
        self.assertEqual(codes[0].start, 0)
        self.assertEqual(codes[0].end, 6)
        self.assertEqual(codes[0].value, '1234/3')
        self.assertEqual(codes[1].start, 8)
        self.assertEqual(codes[1].end, 14)
        self.assertEqual(codes[1].value, '6789/8')

    def test_morphology_error(self):
        result = extractor.transform('12345/3')
        self.assertEquals(result, {})
