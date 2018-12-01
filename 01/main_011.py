import fileinput
from typing import Dict, List, Tuple
import unittest


def process(diffs: List[str]) -> int:
    num_diffs = [(-1 if (x[0] == '-') else 1) * int(x[1:]) for x in diffs]
    return sum(num_diffs)


if __name__ == '__main__':
    lines = []
    for line in fileinput.input():
        lines += [line.strip()]
    print(process(lines))


class Test011(unittest.TestCase):
    def test_1(self):
        self.assertEqual(
            process(['+1', '-2', '+3', '+1']),
            3)

    def test_2(self):
        self.assertEqual(
            process(['+1', '+1', '+1']),
            3)

    def test_3(self):
        self.assertEqual(
            process(['+1', '+1', '-2']),
            0)

    def test_4(self):
        self.assertEqual(
            process(['-1', '-2', '-3']),
            -6)
