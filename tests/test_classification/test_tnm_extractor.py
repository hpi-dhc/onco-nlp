import unittest
from onconlp.classification.tnm import TNMExtractor

class TestTNMExtractor(unittest.TestCase):

    def test_TNM_Simple(self):
        tnm = TNMExtractor()
        tnm.process_document('T1 N1 M0')

if __name__ == '__main__':
    unittest.main()