import unittest
from onconlp.classification.tnm import TNMExtractor

class TestTNMExtractor(unittest.TestCase):

    def assertNull(self, obj, all_but):
        for p in ['T', 'N', 'M', 'L', 'V', 'Pn', 'SX', 'R', 'G']:
            if p not in all_but:
                self.assertIsNone(getattr(obj, p))

    def check_match(self, elem, token, prefix, value, details, start, end):
        self.assertIsNotNone(elem, token)
        self.assertEqual(elem.token, token, token)
        self.assertEqual(elem.prefix, prefix, token)
        self.assertEqual(elem.details, details, token)
        self.assertEqual(elem.value, value, token)
        self.assertEqual(elem.start, start, token)
        self.assertEqual(elem.end, end, token)

    #### Basic tests
    # based on https://www.krebsregister.unibe.ch/unibe/portal/microsites/krebsregister/content/e317889/e336472/e336546/TNM-Klassifikation_MW_22.01.15.pdf

    def check_simple_range(self, component, vrange):
        extractor = TNMExtractor()
        for v in vrange:
            tnms = extractor.transform(v)
            self.assertEqual(len(tnms), 1)
            tnm = tnms[0]
            self.check_match(getattr(tnm, component), v, None, v, {}, 0, len(v))
            self.assertNull(tnm, [component])

    def check_simple_range_negative(self,  component, vrange):
        extractor = TNMExtractor()
        for v in vrange:
            tnms = extractor.transform(v)
            self.assertEqual(len(tnms), 0, '%s should not match' % v )

    def test_tnm_t_simple(self):
        self.check_simple_range('T', 
            ['T0', 'T1', 'T2', 'T3', 'T4', 
             'T1a', 'T1b', 'T1c', 'T1d', 
             'T2a', 'T2b', 'T2c', 'T2d', 
             'T3a', 'T3b', 'T3c', 'T3d', 
             'T4a', 'T4b', 'T4c', 'T4d', 
             'Tis', 'Ta', 'TX'])            

    def test_tnm_t_simple_negative(self):
        self.check_simple_range_negative('T', ['T5', 'T', 'Tb', 'Tc', 'T-'])            

    def test_tnm_n_simple(self):
        self.check_simple_range('N', [
            'N0', 'N1', 'N2', 'N3',
            'N1a', 'N1b', 'N1c', 'N1d', 
            'N2a', 'N2b', 'N2c', 'N2d', 
            'N3a', 'N3b', 'N3c', 'N3d', 
            'NX'
        ])

    def test_tnm_n_simple_negative(self):
        self.check_simple_range_negative('N', ['N4', 'N', 'Na', 'Nis', 'N-'])  

    def test_tnm_n_lymphnodes(self):
        for term in ['N1(1/2)', 'N1 (1/2)', 'N1( 1/2)', 'N1( 1 / 2)', 'N1 ( 1 / 2 )']:
            tnms = TNMExtractor().transform(term)
            self.assertEqual(len(tnms), 1)
            tnm = tnms[0]
            self.check_match(tnm.N, term, None, 'N1', 
                {'lymphnodes_affected': 1, 'lymphnodes_examined': 2}, 
                0, len(term))

    def test_tnm_n_sn(self):
        for term in ['N1(sn)', 'N1 (sn)', 'N1  (sn)', 'N1 ( sn)', 'N1 ( sn )']:
            tnms = TNMExtractor().transform(term)
            self.assertEqual(len(tnms), 1)
            tnm = tnms[0]
            self.check_match(tnm.N, term, None, 'N1', 
                {'other': 'sn'}, 
                0, len(term))

    def test_tnm_n_sn_lymphnodes(self):
        for term in ['N1(1/2sn)', 'N1 (1/2 sn)', 'N1  (sn 1/2)', 'N1 (1/2 sn)', 'N1 ( 1/2 sn )']:
            tnms = TNMExtractor().transform(term)
            self.assertEqual(len(tnms), 1)
            tnm = tnms[0]
            self.check_match(tnm.N, term, None, 'N1', 
                {
                    'lymphnodes_affected': 1, 
                    'lymphnodes_examined': 2,
                    'other': 'sn'
                }, 
                0, len(term))

    def test_tnm_n_affixes(self):
        tnms = TNMExtractor().transform('N0(i-)')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.N, 'N0(i-)', None, 'N0', {'other': 'i-'}, 0, 6)
        tnms = TNMExtractor().transform('N0(i+)')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.N, 'N0(i+)', None, 'N0', {'other': 'i+'}, 0, 6)
        tnms = TNMExtractor().transform('N0(mol-)')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.N, 'N0(mol-)', None, 'N0', {'other': 'mol-'}, 0, 8)
        tnms = TNMExtractor().transform('N0(mol+)')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.N, 'N0(mol+)', None, 'N0', {'other': 'mol+'}, 0, 8)

    def test_tnm_m_simple(self):
        self.check_simple_range('M', 
            ['M0', 'M1', 'M1a', 'M1b', 'MX'])        

    def test_tnm_m_simple_negative(self):
        self.check_simple_range_negative('M', 
            ['M2', 'Ma', 'Mis', 'M'])        

    def test_tnm_grading_simple(self):
        self.check_simple_range('G', 
            ['G1', 'G2', 'G3', 'G4', 'GX'])    

    def test_tnm_grading_simple_negative(self):
        self.check_simple_range_negative('G', 
            ['G0', 'G5', 'G', 'Ga', 'Gis'])

    def test_tnm_residual_simple(self):
        self.check_simple_range('R', 
            ['R0', 'R1', 'R2', 'R2a', 'R2b'])

    def test_tnm_residual_simple_negative(self):
        self.check_simple_range_negative('R', 
            ['R3', 'R', 'Ra', 'RX'])

    def test_tnm_lymphinvasion_simple(self):
        self.check_simple_range('L', 
            ['L0', 'L1', 'LX'])

    def test_tnm_lymphinvasion_simple_negative(self):
        self.check_simple_range_negative('L', 
            ['L2', 'La', 'L'])

    def test_tnm_vene_invasion_simple(self):
        self.check_simple_range('V', 
            ['V0', 'V1', 'V2', 'VX'])

    def test_tnm_vene_invasion_simple_negative(self):
        self.check_simple_range_negative('V', 
            ['V3', 'Va', 'V'])

    def test_tnm_perineural_invasion_simple(self):
        self.check_simple_range('Pn', 
            ['Pn0', 'Pn1', 'PnX'])

    def test_tnm_perineural_simple_negative(self):
        self.check_simple_range_negative('Pn', 
            ['Pn2', 'Pn', 'P'])

    def test_tnm_perineural_vs_lypmh(self):
        tnm_extractor = TNMExtractor()
        
        tnms = tnm_extractor.transform('PN1')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.N, 'N1', None, 'N1', {}, 1, 3)

        tnms = tnm_extractor.transform('Pn1')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.Pn, 'Pn1', None, 'Pn1', {}, 0, 3)

        tnms = tnm_extractor.transform('pN1')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.N, 'pN1', ['p'], 'N1', {}, 0, 3)

        tnms = tnm_extractor.transform('pn1')
        self.assertEqual(len(tnms), 0)

    def test_tnm_multitoken(self):
        tnms = TNMExtractor().transform('T1 N1 M0')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'T1', None, 'T1', {}, 0, 2)
        self.check_match(tnm.N, 'N1', None, 'N1', {}, 3, 5)
        self.check_match(tnm.M, 'M0', None, 'M0', {}, 6, 8)
        self.assertNull(tnm, ['T', 'N', 'M'])
    
    def test_tnm_prefix(self):
        tnms = TNMExtractor().transform('pT1 cN1')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'pT1', ['p'], 'T1', {}, 0, 3)
        self.check_match(tnm.N, 'cN1', ['c'], 'N1', {}, 4, 7)
        self.assertNull(tnm, ['T', 'N'])
   
    #### Real-world examples

    def test_tnm_example_1(self):
        tnms = TNMExtractor().transform('cT4 cN2 cM0 G3')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'cT4', ['c'], 'T4', {}, 0, 3)
        self.check_match(tnm.N, 'cN2', ['c'], 'N2', {}, 4, 7)
        self.check_match(tnm.M, 'cM0', ['c'], 'M0', {}, 8, 11)
        self.check_match(tnm.G, 'G3', None, 'G3', {}, 12, 14)
        self.assertNull(tnm, ['T', 'N', 'M', 'G'])

    def test_tnm_example_2(self):
        tnms = TNMExtractor().transform('cT4b cN2a cM0 G2')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'cT4b', ['c'], 'T4b', {}, 0, 4)
        self.check_match(tnm.N, 'cN2a', ['c'], 'N2a', {}, 5, 9)
        self.check_match(tnm.M, 'cM0', ['c'], 'M0', {}, 10, 13)
        self.check_match(tnm.G, 'G2', None, 'G2', {}, 14, 16)
        self.assertNull(tnm, ['T', 'N', 'M', 'G'])

    def test_tnm_example_3(self):
        tnms = TNMExtractor().transform('pT4b pN2b (18/25) cM0 G3 pL1 pV1 Pn0')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'pT4b', ['c'], 'T4b', {}, 0, 4)
        self.check_match(tnm.N, 'pN2b', ['c'], 'N2a', {}, 5, 17)
        self.check_match(tnm.M, 'cM0', ['c'], 'M0', {}, 18, 21)
        self.check_match(tnm.G, 'G3', None, 'G3', {}, 22, 23)
        self.check_match(tnm.L, 'pL1', ['p'], 'L1', {}, 25, 28)
        self.check_match(tnm.V, 'pV1', ['p'], 'V1', {}, 29, 32)
        self.check_match(tnm.Pn, 'Pn0', None, 'Pn0', {}, 33, 36)
        self.assertNull(tnm, ['T', 'N', 'M', 'G', 'L', 'V', 'Pn'])

    def test_TNM_Lymphnodes(self):
        tnms = TNMExtractor().transform('pT1 pN1 (5/13)')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'pT1', ['p'], 'T1', {}, 0, 3)
        self.check_match(tnm.N, 'pN1 (5/13)', ['p'], 'N1', 
            {'lymphnodes_affected': 5, 'lymphnodes_examined': 13}, 4, 14)
        self.assertNull(tnm, ['T', 'N'])

    def test_TNM_Prefix_Neoadjuvant(self):
        tnms = TNMExtractor().transform('ypT0N0M0')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'ypT0', ['y', 'p'], 'T0', {}, 0, 4)
        self.check_match(tnm.N, 'N0', None, 'N0', {}, 4, 6)
        self.check_match(tnm.M, 'M0', None, 'M0', {}, 6, 8)
        self.assertNull(tnm, ['T', 'N', 'M'])

    def test_TNM_Prefix_Rezidiv(self):
        tnms = TNMExtractor().transform('rpT2pN1M0')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'rpT2', ['r', 'p'], 'T2', {}, 0, 4)
        self.check_match(tnm.N, 'pN1', ['p'], 'N1', {}, 4, 7)
        self.check_match(tnm.M, 'M0', None, 'M0', {}, 7, 9)
        self.assertNull(tnm, ['T', 'N', 'M'])

    def test_TNM_single_sentence(self):
        text = """TNM (8. Aufl.): pT1b, pNX, L0, V0
        Grading: G2

        R-Klassifikation (lokal): R0 """
        tnms = TNMExtractor().transform(text)

        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'pT1b', ['p'], 'T1b', {}, 16, 20)
        self.check_match(tnm.N, 'pNX', ['p'], 'NX', {}, 22, 25)
        self.check_match(tnm.L, 'L0', None, 'L0', {}, 27, 29)
        self.check_match(tnm.V, 'V0', None, 'V0', {}, 31, 33)
        self.check_match(tnm.G, 'G2', None, 'G2', {}, 51, 53)
        self.check_match(tnm.R, 'R0', None, 'R0', {}, 89, 91)
        self.assertNull(tnm, ['T', 'N', 'L', 'V', 'G', 'R'])

    def test_TNM_grading_1(self):
        text = "2. Grading (1/2/3) G3 "
        tnms = TNMExtractor().transform(text)

        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.G, 'G3', None, 'G3', {}, 19, 21)
        self.assertNull(tnm, ['G'])

    def test_TNM_grading_2(self):
        text = "2. Grading (1/2/3) G2 "
        tnms = TNMExtractor().transform(text)

        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.G, 'G2', None, 'G2', {}, 19, 21)
        self.assertNull(tnm, ['G'])

    def test_TNM_grading_3(self):
        text = "2. Grading (1, 2, 3) G2"
        tnms = TNMExtractor().transform(text)

        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.G, 'G2', None, 'G2', {}, 21, 23)
        self.assertNull(tnm, ['G'])

    def test_TNM_grading_4(self):
        text = "2. Grading (1, 2, 3) G3 "
        tnms = TNMExtractor().transform(text)

        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.G, 'G3', None, 'G3', {}, 21, 23)
        self.assertNull(tnm, ['G'])
       

if __name__ == '__main__':
    unittest.main()