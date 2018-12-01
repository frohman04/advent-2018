import fileinput
from typing import Dict, List, Tuple
import unittest


def process(diffs: List[str]) -> int:
    num_diffs = [(-1 if (x[0] == '-') else 1) * int(x[1:]) for x in diffs]
    seen_freqs = set([0])
    freq = 0
    idx = 0
    while True:
        freq += num_diffs[idx]

        if freq in seen_freqs:
            break
        seen_freqs.add(freq)

        idx += 1
        if idx >= len(num_diffs):
            idx -= len(num_diffs)

    return freq


if __name__ == '__main__':
    lines = []
    for line in fileinput.input():
        lines += [line.strip()]
    print(process(lines))


class Test012(unittest.TestCase):
    def test_1(self):
        self.assertEqual(
            process(['+1', '-2', '+3', '+1']),
            2)

    def test_2(self):
        self.assertEqual(
            process(['+1', '-1']),
            0)

    def test_3(self):
        self.assertEqual(
            process(['+3', '+3', '+4', '-2', '-4']),
            10)

    def test_4(self):
        self.assertEqual(
            process(['-6', '+3', '+8', '+5', '-6']),
            5)

    def test_5(self):
        self.assertEqual(
            process(['+7', '+7', '-2', '-7', '-4']),
            14)
