from collections import Counter
import fileinput
from typing import List, Tuple
import unittest


def checksum_one(id: str) -> Tuple[bool, bool]:
    rev = {b: a for a, b in Counter(id).items()}
    return 2 in rev, 3 in rev


def checksum(ids: List[str]) -> int:
    count_two = 0
    count_three = 0
    for id in ids:
        has_two, has_three = checksum_one(id)
        if has_two:
            count_two += 1
        if has_three:
            count_three += 1
    return count_two * count_three


if __name__ == '__main__':
    lines = []
    for line in fileinput.input():
        lines += [line.strip()]
    print(checksum(lines))


class Test021(unittest.TestCase):
    def test_one_1(self):
        self.assertEqual(
            checksum_one('abcdef'),
            (False, False))

    def test_one_2(self):
        self.assertEqual(
            checksum_one('bababc'),
            (True, True))

    def test_one_3(self):
        self.assertEqual(
            checksum_one('abbcde'),
            (True, False))

    def test_one_4(self):
        self.assertEqual(
            checksum_one('abcccd'),
            (False, True))

    def test_one_5(self):
        self.assertEqual(
            checksum_one('aabcdd'),
            (True, False))

    def test_one_6(self):
        self.assertEqual(
            checksum_one('abcdee'),
            (True, False))

    def test_one_7(self):
        self.assertEqual(
            checksum_one('ababab'),
            (False, True))

    def test_1(self):
        self.assertEqual(
            checksum([
                'abcdef',
                'bababc',
                'abbcde',
                'abcccd',
                'aabcdd',
                'abcdee',
                'ababab'
            ]),
            12)
