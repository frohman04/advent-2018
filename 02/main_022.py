import fileinput
import itertools
from typing import List
import unittest


def munge_id(id: str) -> List[str]:
    munged = []
    for i in range(len(id)):
        munged.append(id[:i] + id[i + 1:])
    return munged


def find(ids: List[str]) -> str:
    munged = {}
    for id in ids:
        munged[id] = munge_id(id)
    for item1, item2 in itertools.combinations(munged.items(), 2):
        for i in range(len(item1[1])):
            if item1[1][i] == item2[1][i]:
                return item1[1][i]


if __name__ == '__main__':
    lines = []
    for line in fileinput.input():
        lines += [line.strip()]
    print(find(lines))


class Test022(unittest.TestCase):
    def test_munge(self):
        self.assertEqual(
            munge_id('abcde'),
            ['bcde', 'acde', 'abde', 'abce', 'abcd'])

    def test_find(self):
        self.assertEqual(
            find([
                'abcde',
                'fghij',
                'klmno',
                'pqrst',
                'fguij',
                'axcye',
                'wvxyz'
            ]),
            'fgij')
