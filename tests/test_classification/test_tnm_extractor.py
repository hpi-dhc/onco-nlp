import unittest
from onconlp.classification.tnm import TNMExtractor

class TestTNMExtractor(unittest.TestCase):

    def assertNull(self, obj, all_but):
        for p in ['T', 'N', 'M', 'L', 'V', 'Pn', 'SX', 'R', 'G']:
            if p not in all_but:
                self.assertIsNone(getattr(obj, p))

    def check_match(self, elem, token, prefix, value, start, end):
        self.assertIsNotNone(elem)
        self.assertEqual(elem.token, token)
        self.assertEqual(elem.prefix, prefix)
        self.assertEqual(elem.value, value)
        self.assertEqual(elem.start, start)
        self.assertEqual(elem.end, end)

    #### Basic tests

    def test_TNM_Single(self):
        tnms = TNMExtractor().transform('T1')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'T1', None, 'T1', 0, 2)
        self.assertNull(tnm, ['T'])

    def test_TNM_Simple(self):
        tnms = TNMExtractor().transform('T1 N1 M0')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'T1', None, 'T1', 0, 2)
        self.check_match(tnm.N, 'N1', None, 'N1', 3, 5)
        self.check_match(tnm.M, 'M0', None, 'M0', 6, 8)
        self.assertNull(tnm, ['T', 'N', 'M'])
    
    def test_TNM_Prefix(self):
        tnms = TNMExtractor().transform('pT1 cN1')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'pT1', ['p'], 'T1', 0, 3)
        self.check_match(tnm.N, 'cN1', ['c'], 'N1', 4, 7)
        self.assertNull(tnm, ['T', 'N'])

    def test_TNM_Lymphnodes(self):
        tnms = TNMExtractor().transform('pT1 pN1 (5/13)')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'pT1', ['p'], 'T1', 0, 3)
        self.check_match(tnm.N, 'pN1 (5/13)', ['p'], 'N1', 4, 14)
        self.assertNull(tnm, ['T', 'N'])

    #### Real-world examples

    def test_TNM_Prefix_Neoadjuvant(self):
        tnms = TNMExtractor().transform('ypT0N0M0')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'ypT0', ['y', 'p'], 'T0', 0, 4)
        self.check_match(tnm.N, 'N0', None, 'N0', 4, 6)
        self.check_match(tnm.M, 'M0', None, 'M0', 6, 8)
        self.assertNull(tnm, ['T', 'N', 'M'])

    def test_TNM_Prefix_Rezidiv(self):
        tnms = TNMExtractor().transform('rpT2pN1M0')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'rpT2', ['r', 'p'], 'T2', 0, 4)
        self.check_match(tnm.N, 'pN1', ['p'], 'N1', 4, 7)
        self.check_match(tnm.M, 'M0', None, 'M0', 7, 9)
        self.assertNull(tnm, ['T', 'N', 'M'])

    def test_TNM_single_sentence(self):
        text = """TNM (8. Aufl.): pT1b, pNX, L0, V0
        Grading: G2

        R-Klassifikation (lokal): R0 """
        tnms = TNMExtractor().transform(text)

        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'pT1b', ['p'], 'T1b', 16, 20)
        self.check_match(tnm.N, 'pNX', ['p'], 'NX', 22, 25)
        self.check_match(tnm.L, 'L0', None, 'L0', 27, 29)
        self.check_match(tnm.V, 'V0', None, 'V0', 31, 33)
        self.check_match(tnm.G, 'G2', None, 'G2', 51, 53)
        self.check_match(tnm.R, 'R0', None, 'R0', 89, 91)
        self.assertNull(tnm, ['T', 'N', 'L', 'V', 'G', 'R'])

    def test_TNM_grading_1(self):
        text = "2. Grading (1/2/3) G3 "
        tnms = TNMExtractor().transform(text)

        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.G, 'G3', None, 'G3', 19, 21)
        self.assertNull(tnm, ['G'])

    def test_TNM_grading_2(self):
        text = "2. Grading (1/2/3) G2 "
        tnms = TNMExtractor().transform(text)

        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.G, 'G2', None, 'G2', 19, 21)
        self.assertNull(tnm, ['G'])

    def test_TNM_grading_3(self):
        text = "2. Grading (1, 2, 3) G2"
        tnms = TNMExtractor().transform(text)

        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.G, 'G2', None, 'G2', 21, 23)
        self.assertNull(tnm, ['G'])

    def test_TNM_grading_4(self):
        text = "2. Grading (1, 2, 3) G3 "
        tnms = TNMExtractor().transform(text)

        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.G, 'G3', None, 'G3', 21, 23)
        self.assertNull(tnm, ['G'])
       

if __name__ == '__main__':
    unittest.main()