import unittest

class SampleSuite(unittest.TestCase):
    def test_feature_one(self):
        self.assertEqual(1 + 1, 2)
        self.assertTrue(True)

    def test_feature_two(self):
        assert 10 > 5

    @unittest.skip("Skipped during refactor")
    def test_feature_three(self):
        pass
