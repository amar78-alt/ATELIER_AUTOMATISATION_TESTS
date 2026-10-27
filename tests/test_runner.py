import unittest

from tester.runner import _percentile


class PercentileTests(unittest.TestCase):
    def test_empty_values(self):
        self.assertEqual(_percentile([], 0.95), 0.0)

    def test_p95_of_sorted_small_sample(self):
        self.assertEqual(_percentile([10, 20, 30, 40, 50, 60], 0.95), 60)

    def test_percentile_is_bounded(self):
        self.assertEqual(_percentile([7, 9], 0.95), 9)


if __name__ == "__main__":
    unittest.main()
