import unittest

from entropy import filter_words


class TestMinRequiredFix(unittest.TestCase):
    def test_spend_case(self):
        # Scenario from bug report:
        # First guess 'raise' produced yellow s at pos3 and e at pos4
        # Second guess 'spelt' produced greens at pos0,1,2 (s,p,e)
        possible = ["spend"]
        green = {0: 's', 1: 'p', 2: 'e'}
        yellow = {'s': {3}, 'e': {4}}
        gray = {'l', 'r', 'i', 't', 'a'}
        min_required = {'s': 1, 'e': 1, 'p': 1}

        filtered = filter_words(possible, green, yellow, gray, min_required=min_required)
        self.assertIn('spend', filtered)


if __name__ == '__main__':
    unittest.main()
