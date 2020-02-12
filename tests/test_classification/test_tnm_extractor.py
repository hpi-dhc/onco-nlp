import unittest
from onconlp.classification.tnm import TNMExtractor

class TestTNMExtractor(unittest.TestCase):

    extractor = TNMExtractor()

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
        for v in vrange:
            tnms = self.extractor.transform(v)
            self.assertEqual(len(tnms), 1)
            tnm = tnms[0]
            self.check_match(getattr(tnm, component), v, [], v, {}, 0, len(v))
            self.assertNull(tnm, [component])

    def check_simple_range_negative(self,  component, vrange):
        for v in vrange:
            tnms = self.extractor.transform(v)
            self.assertEqual(len(tnms), 0, '%s should not match' % v )

    def test_tnm_t_simple(self):
        self.check_simple_range('T', 
            ['T0', 'T1', 'T2', 'T3', 'T4', 
             'T1a', 'T1b', 'T1c', 'T1d', 
             'T2a', 'T2b', 'T2c', 'T2d', 
             'T3a', 'T3b', 'T3c', 'T3d', 
             'T4a', 'T4b', 'T4c', 'T4d', 
             'Tis', 'Ta', 'TX', 'Tx'])            

    def test_tnm_t_simple_negative(self):
        self.check_simple_range_negative('T', ['T5', 'T', 'Tb', 'Tc', 'T-'])            

    def test_tnm_n_simple(self):
        self.check_simple_range('N', [
            'N0', 'N1', 'N2', 'N3',
            'N1a', 'N1b', 'N1c', 'N1d', 
            'N2a', 'N2b', 'N2c', 'N2d', 
            'N3a', 'N3b', 'N3c', 'N3d', 
            'NX', 'Nx'
        ])

    def test_tnm_n_simple_negative(self):
        self.check_simple_range_negative('N', ['N4', 'N', 'Na', 'Nis', 'N-'])  

    def test_tnm_n_lymphnodes(self):
        for term in ['N1(1/2)', 'N1 (1/2)', 'N1( 1/2)', 'N1( 1 / 2)', 'N1 ( 1 / 2 )']:
            tnms = self.extractor.transform(term)
            self.assertEqual(len(tnms), 1)
            tnm = tnms[0]
            self.check_match(tnm.N, term, [], 'N1', 
                {'lymphnodes_affected': 1, 'lymphnodes_examined': 2}, 
                0, len(term))

    def test_tnm_n_sn(self):
        for term in ['N1(sn)', 'N1 (sn)', 'N1  (sn)', 'N1 ( sn)', 'N1 ( sn )']:
            tnms = self.extractor.transform(term)
            self.assertEqual(len(tnms), 1)
            tnm = tnms[0]
            self.check_match(tnm.N, term, [], 'N1', 
                {'other': 'sn'}, 
                0, len(term))

    def test_tnm_n_sn_lymphnodes(self):
        for term in ['N1(1/2sn)', 'N1 (1/2 sn)', 'N1  (sn 1/2)', 'N1 (1/2 sn)', 'N1 ( 1/2 sn )']:
            tnms = self.extractor.transform(term)
            self.assertEqual(len(tnms), 1)
            tnm = tnms[0]
            self.check_match(tnm.N, term, [], 'N1', 
                {
                    'lymphnodes_affected': 1, 
                    'lymphnodes_examined': 2,
                    'other': 'sn'
                }, 
                0, len(term))

    def test_no_parantheses(self):
        extractor = TNMExtractor(detect_parantheses=False)
        tnms = extractor.transform('N0(i-)')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.N, 'N0', [], 'N0', {}, 0, 2)
         
        tnms = extractor.transform('T1 (Erläuterung)')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'T1', [], 'T1', {}, 0, 2)

    def test_tnm_n_affixes(self):
        tnms = self.extractor.transform('N0(i-)')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.N, 'N0(i-)', [], 'N0', {'other': 'i-'}, 0, 6)
        tnms = self.extractor.transform('N0(i+)')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.N, 'N0(i+)', [], 'N0', {'other': 'i+'}, 0, 6)
        tnms = self.extractor.transform('N0(mol-)')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.N, 'N0(mol-)', [], 'N0', {'other': 'mol-'}, 0, 8)
        tnms = self.extractor.transform('N0(mol+)')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.N, 'N0(mol+)', [], 'N0', {'other': 'mol+'}, 0, 8)

    def test_tnm_m_simple(self):
        self.check_simple_range('M', 
            ['M0', 'M1', 'M1a', 'M1b', 'MX', 'Mx'])        

    def test_tnm_m_simple_negative(self):
        self.check_simple_range_negative('M', 
            ['M2', 'Ma', 'Mis', 'M'])        

    def test_tnm_grading_simple(self):
        self.check_simple_range('G', 
            ['G1', 'G2', 'G3', 'G4', 'GX', 'Gx'])    

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

    def test_tnm_words(self):
        tnms = self.extractor.transform('Tissue')
        self.assertEqual(len(tnms), 0)
        tnms = self.extractor.transform('Target')
        self.assertEqual(len(tnms), 0)

    def test_tnm_perineural_vs_lypmh(self):        
        # Controverial, but genes would match if too lax
        tnms = self.extractor.transform('PN1')
        self.assertEqual(len(tnms), 0)

        tnms = self.extractor.transform('Pn1')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.Pn, 'Pn1', [], 'Pn1', {}, 0, 3)

        tnms = self.extractor.transform('pN1')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.N, 'pN1', ['p'], 'N1', {}, 0, 3)

        tnms = self.extractor.transform('pn1')
        self.assertEqual(len(tnms), 0)

    def test_tnm_multitoken(self):
        tnms = self.extractor.transform('T1 N1 M0')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'T1', [], 'T1', {}, 0, 2)
        self.check_match(tnm.N, 'N1', [], 'N1', {}, 3, 5)
        self.check_match(tnm.M, 'M0', [], 'M0', {}, 6, 8)
        self.assertNull(tnm, ['T', 'N', 'M'])
    
    def test_tnm_prefix(self):
        tnms = self.extractor.transform('pT1 cN1')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'pT1', ['p'], 'T1', {}, 0, 3)
        self.check_match(tnm.N, 'cN1', ['c'], 'N1', {}, 4, 7)
        self.assertNull(tnm, ['T', 'N'])

    def test_tnm_prefix_multiple(self):
        tnms = self.extractor.transform('acT1 uN1 yrapM1')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'acT1', ['a', 'c'], 'T1', {}, 0, 4)
        self.check_match(tnm.N, 'uN1', ['u'], 'N1', {}, 5, 8)
        self.check_match(tnm.M, 'yrapM1', ['y', 'r', 'a', 'p'], 'M1', {}, 9, 15)
        self.assertNull(tnm, ['T', 'N', 'M'])

    def test_tnm_prefix_invalid(self):
        tnms = self.extractor.transform('puT1 puT1 yraaM1')
        self.assertEqual(len(tnms), 0)
   
    #### Corner cases

    def test_tnm_context_negative(self):
        self.check_simple_range_negative('T', ['AT2', '1T1'])

    def test_tnm_context_special_char(self):
        for t in ['(T1', '-T1', '[T1', '$T1', '/T1', '\T1', '§T1', '(T1', ')T1', ',T1']:
            tnms = self.extractor.transform(t)
            self.assertEqual(len(tnms), 1)
            tnm = tnms[0]
            self.check_match(tnm.T, 'T1', [], 'T1', {}, 1, 3)
    

    #### Real-world examples

    def test_tnm_example_1(self):
        tnms = self.extractor.transform('cT4 cN2 cM0 G3')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'cT4', ['c'], 'T4', {}, 0, 3)
        self.check_match(tnm.N, 'cN2', ['c'], 'N2', {}, 4, 7)
        self.check_match(tnm.M, 'cM0', ['c'], 'M0', {}, 8, 11)
        self.check_match(tnm.G, 'G3', [], 'G3', {}, 12, 14)
        self.assertNull(tnm, ['T', 'N', 'M', 'G'])

    def test_tnm_example_2(self):
        tnms = self.extractor.transform('cT4b cN2a cM0 G2')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'cT4b', ['c'], 'T4b', {}, 0, 4)
        self.check_match(tnm.N, 'cN2a', ['c'], 'N2a', {}, 5, 9)
        self.check_match(tnm.M, 'cM0', ['c'], 'M0', {}, 10, 13)
        self.check_match(tnm.G, 'G2', [], 'G2', {}, 14, 16)
        self.assertNull(tnm, ['T', 'N', 'M', 'G'])

    def test_tnm_example_3(self):
        tnms = self.extractor.transform('pT4b pN2b (18/25) cM0 G3 pL1 pV1 Pn0')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'pT4b', ['p'], 'T4b', {}, 0, 4)
        self.check_match(tnm.N, 'pN2b (18/25)', ['p'], 'N2b', 
            {'lymphnodes_affected': 18, 'lymphnodes_examined': 25}, 5, 17)
        self.check_match(tnm.M, 'cM0', ['c'], 'M0', {}, 18, 21)
        self.check_match(tnm.G, 'G3', [], 'G3', {}, 22, 24)
        self.check_match(tnm.L, 'pL1', ['p'], 'L1', {}, 25, 28)
        self.check_match(tnm.V, 'pV1', ['p'], 'V1', {}, 29, 32)
        self.check_match(tnm.Pn, 'Pn0', [], 'Pn0', {}, 33, 36)
        self.assertNull(tnm, ['T', 'N', 'M', 'G', 'L', 'V', 'Pn'])

    def test_TNM_Lymphnodes(self):
        tnms = self.extractor.transform('pT1 pN1 (5/13)')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'pT1', ['p'], 'T1', {}, 0, 3)
        self.check_match(tnm.N, 'pN1 (5/13)', ['p'], 'N1', 
            {'lymphnodes_affected': 5, 'lymphnodes_examined': 13}, 4, 14)
        self.assertNull(tnm, ['T', 'N'])

    def test_TNM_Prefix_Neoadjuvant(self):
        tnms = self.extractor.transform('ypT0N0M0')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'ypT0', ['y', 'p'], 'T0', {}, 0, 4)
        self.check_match(tnm.N, 'N0', [], 'N0', {}, 4, 6)
        self.check_match(tnm.M, 'M0', [], 'M0', {}, 6, 8)
        self.assertNull(tnm, ['T', 'N', 'M'])

    def test_TNM_Prefix_Rezidiv(self):
        tnms = self.extractor.transform('rpT2pN1M0')
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'rpT2', ['r', 'p'], 'T2', {}, 0, 4)
        self.check_match(tnm.N, 'pN1', ['p'], 'N1', {}, 4, 7)
        self.check_match(tnm.M, 'M0', [], 'M0', {}, 7, 9)
        self.assertNull(tnm, ['T', 'N', 'M'])

    def test_TNM_single_sentence(self):
        text = """TNM (8. Aufl.): pT1b, pNX, L0, V0
        Grading: G2

        R-Klassifikation (lokal): R0 """
        tnms = self.extractor.transform(text)

        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'pT1b', ['p'], 'T1b', {}, 16, 20)
        self.check_match(tnm.N, 'pNX', ['p'], 'NX', {}, 22, 25)
        self.check_match(tnm.L, 'L0', [], 'L0', {}, 27, 29)
        self.check_match(tnm.V, 'V0', [], 'V0', {}, 31, 33)
        self.check_match(tnm.G, 'G2', [], 'G2', {}, 51, 53)
        self.check_match(tnm.R, 'R0', [], 'R0', {}, 89, 91)
        self.assertNull(tnm, ['T', 'N', 'L', 'V', 'G', 'R'])

    def test_TNM_grading_1(self):
        text = "2. Grading (1/2/3) G3 "
        tnms = self.extractor.transform(text)

        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.G, 'G3', [], 'G3', {}, 19, 21)
        self.assertNull(tnm, ['G'])

    def test_TNM_grading_2(self):
        text = "2. Grading (1/2/3) G2 "
        tnms = self.extractor.transform(text)

        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.G, 'G2', [], 'G2', {}, 19, 21)
        self.assertNull(tnm, ['G'])

    def test_TNM_grading_3(self):
        text = "2. Grading (1, 2, 3) G2"
        tnms = self.extractor.transform(text)

        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.G, 'G2', [], 'G2', {}, 21, 23)
        self.assertNull(tnm, ['G'])

    def test_TNM_grading_4(self):
        text = "2. Grading (1, 2, 3) G3 "
        tnms = self.extractor.transform(text)
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.G, 'G3', [], 'G3', {}, 21, 23)
        self.assertNull(tnm, ['G'])
       
    def test_histo_lymph_1(self):
        text = "UICC-Klassifikation (8. Auflage, 2017) 16. pT2, pN1(2/22), G2, L1, V0, Pn1, R0 (lokal) "
        tnms = self.extractor.transform(text)
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'pT2', ['p'], 'T2', {}, 43, 46)
        self.check_match(tnm.N, 'pN1(2/22)', ['p'], 'N1', {
            "lymphnodes_affected" : 2, "lymphnodes_examined" : 22}, 48, 57)
        self.check_match(tnm.G, 'G2', [], 'G2', {}, 59, 61)
        self.check_match(tnm.L, 'L1', [], 'L1', {}, 63, 65)        
        self.check_match(tnm.V, 'V0', [], 'V0', {}, 67, 69)
        self.check_match(tnm.Pn, 'Pn1', [], 'Pn1', {}, 71, 74)
        self.check_match(tnm.R, 'R0 (lokal)', [], 'R0', {
            "other" : 'lokal' }, 76, 86)
        self.assertIsNone(tnm.M)
        self.assertIsNone(tnm.SX)

    def test_histo_lymph_2(self):
        text = "UICC-Klassifikation (8. Auflage, 2017): 14. pT2, pN1 (3/13, max. 1,8 cm), L1, V0, Pn1, R1 (dorsal), CRM positiv"
        tnms = self.extractor.transform(text)
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'pT2', ['p'], 'T2', {}, 44, 47)
        self.check_match(tnm.N, 'pN1 (3/13, max. 1,8 cm)', ['p'], 'N1', {
            "lymphnodes_affected" : 3, "lymphnodes_examined" : 13, "other" : 'max. 1,8 cm'}, 49, 72)
        self.check_match(tnm.L, 'L1', [], 'L1', {}, 74, 76)        
        self.check_match(tnm.V, 'V0', [], 'V0', {}, 78, 80)
        self.check_match(tnm.Pn, 'Pn1', [], 'Pn1', {}, 82, 85)
        self.check_match(tnm.R, 'R1 (dorsal)', [], 'R1', {
            "other" : 'dorsal' }, 87, 98)
        self.assertIsNone(tnm.M)
        self.assertIsNone(tnm.G)
        self.assertIsNone(tnm.SX)

    def test_histo_lymph_3(self):
        text = "UICC-Klassifikation (8. Auflage, 2017): 20. pT3, pN2(4/21), pMX - G2, L1, V1, Pn1, R1"
        tnms = self.extractor.transform(text)
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'pT3', ['p'], 'T3', {}, 44, 47)
        self.check_match(tnm.N, 'pN2(4/21)', ['p'], 'N2', {
            "lymphnodes_affected" : 4, "lymphnodes_examined" : 21
        }, 49, 58)
        self.check_match(tnm.M, 'pMX', ['p'], 'MX', {}, 60, 63)
        self.check_match(tnm.G, 'G2', [], 'G2', {}, 66, 68)
        self.check_match(tnm.L, 'L1', [], 'L1', {}, 70, 72)
        self.check_match(tnm.V, 'V1', [], 'V1', {}, 74, 76)
        self.check_match(tnm.Pn, 'Pn1', [], 'Pn1', {}, 78, 81)
        self.check_match(tnm.R, 'R1', [], 'R1', {}, 83, 85)
        self.assertIsNone(tnm.SX)

    def test_histo_lymph_4(self):
        text = "UICC-Klassifikation (8. Auflage, 2017): 19. pT3 (5 cm), pN1(2/12), Pn1, L0, V1, G2, R1 (Gallengangs- und Pankreasabsetzungsrand)"
        tnms = self.extractor.transform(text)
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'pT3 (5 cm)', ['p'], 'T3', {"other" : "5 cm"}, 44, 54)
        self.check_match(tnm.N, 'pN1(2/12)', ['p'], 'N1', {
            "lymphnodes_affected" : 2, "lymphnodes_examined" : 12
        }, 56, 65)
        self.check_match(tnm.Pn, 'Pn1', [], 'Pn1', {}, 67, 70)
        self.check_match(tnm.L, 'L0', [], 'L0', {}, 72, 74)
        self.check_match(tnm.V, 'V1', [], 'V1', {}, 76, 78)
        self.check_match(tnm.G, 'G2', [], 'G2', {}, 80, 82)
        self.check_match(tnm.R, 'R1 (Gallengangs- und Pankreasabsetzungsrand)', 
            [], 'R1', {"other" : 'Gallengangs- und Pankreasabsetzungsrand'}, 84, 128)
        self.assertIsNone(tnm.M)
        self.assertIsNone(tnm.SX)

    def test_complex(self):
        text = "TNM (7.Aufl.): pT2c, MX (0/2 sn), Grading: GX R-Klassifikation (lokal): R0 ICD-O (3. Aufl.): 8522/3 ICD-10: C 49.9"
        tnms = self.extractor.transform(text)
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'pT2c', ['p'], 'T2c', {}, 15, 19)
        self.check_match(tnm.M, 'MX (0/2 sn)', [], 'MX', {'other' : '0/2 sn'}, 21, 32)
        self.check_match(tnm.G, 'GX', [], 'GX', {}, 43, 45)
        self.check_match(tnm.R, 'R0', [], 'R0', {}, 72, 74)

    def test_resection_1(self):
        text = "11. R-Status 0 "
        tnms = self.extractor.transform(text)
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.R, 'R-Status 0', [], 'R0', {}, 4, 14)

    def test_resection_2(self):
        text = "8. R-Status 1 (intraparenchymatöser Absetzungsrand)"
        tnms = self.extractor.transform(text)
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.R, 'R-Status 1 (intraparenchymatöser Absetzungsrand)', [], 'R1', 
            {"other": 'intraparenchymatöser Absetzungsrand'}, 3, 51)

    def test_v_status(self):
        text = "V-Status 1"
        tnms = self.extractor.transform(text)
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.V, 'V-Status 1', [], 'V1', {}, 0, 10)

    def test_spaces(self):
        text = "Tumorstadium: T 2, pN X, pM X - G-II."
        tnms = self.extractor.transform(text)
        self.assertEqual(len(tnms), 0)

        ex = TNMExtractor(language='de', allow_spaces=True)
        tnms = ex.transform(text)
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'T 2', [], 'T2', {}, 14, 17)
        self.check_match(tnm.N, 'pN X', ['p'], 'NX', {}, 19, 23)
        self.check_match(tnm.M, 'pM X', ['p'], 'MX', {}, 25, 29)
        self.assertIsNone(tnm.G)

    def test_merge(self):
        text = "R0 T-Status T2 pT2 N0"
        tnms = self.extractor.transform(text)
        self.assertEqual(len(tnms), 2)
        tnm = tnms[0]
        self.check_match(tnm.T, 'T2', [], 'T2', {}, 12, 14)
        self.check_match(tnm.R, 'R0', [], 'R0', {}, 0, 2)
        self.assertIsNone(tnm.N)
        self.assertFalse(tnm.merged)

        tnm = tnms[1]
        self.check_match(tnm.T, 'pT2', ['p'], 'T2', {}, 15, 18)
        self.check_match(tnm.N, 'N0', [], 'N0', {}, 19, 21)
        self.assertIsNone(tnm.R)
        self.assertFalse(tnm.merged)

        ex = TNMExtractor(language='de', merge_matches=True)
        tnms = ex.transform(text)
        tnm = tnms[0]
        self.assertEqual(len(tnms), 1)
        self.check_match(tnm.T, 'pT2', ['p'], 'T2', {}, 15, 18)
        self.check_match(tnm.R, 'R0', [], 'R0', {}, 0, 2)
        self.check_match(tnm.N, 'N0', [], 'N0', {}, 19, 21)
        self.assertTrue(tnm.merged)

    def test_range(self):
        text = "pNX/0"
        tnms = self.extractor.transform(text)
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.N, 'pNX/0', ['p'], 'NX/0', {}, 0, 5)

        text = "cT2-4"
        tnms = self.extractor.transform(text)
        self.assertEqual(len(tnms), 1)
        tnm = tnms[0]
        self.check_match(tnm.T, 'cT2-4', ['c'], 'T2-4', {}, 0, 5)


if __name__ == '__main__':
    unittest.main()