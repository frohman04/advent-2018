from collections import defaultdict
import fileinput
import re
from typing import List, Type, TypeVar
import unittest

T = TypeVar('T', bound='Claim')


class Claim(object):
    PARSER = re.compile(r'#([0-9]+) @ ([0-9]+),([0-9]+): ([0-9]+)x([0-9]+)')

    def __init__(self, id: int, left: int, top: int, width: int, height: int):
        self.id = id
        self.left = left
        self.top = top
        self.width = width
        self.height = height

    @classmethod
    def from_line(cls: Type[T], line: str) -> T:
        for matches in cls.PARSER.findall(line):
            return Claim(*[int(x) for x in matches])

    def __repr__(self):
        return 'Claim({}, {}, {}, {}, {})'.format(
            self.id, self.left, self.top, self.width, self.height)

    def __eq__(self, other):
        return (self.id == other.id and
                self.left == other.left and
                self.top == other.top and
                self.width == other.width and
                self.height == other.height)


def parse(lines: List[str]) -> List[Claim]:
    return [Claim.from_line(x) for x in lines]


def cover(claims: List[Claim]) -> int:
    ids_per_square = defaultdict(lambda: list())
    for claim in claims:
        for x in range(claim.left, claim.width + claim.left):
            for y in range(claim.top, claim.height + claim.top):
                ids_per_square[x, y].append(claim.id)

    counts_per_id = defaultdict(lambda: list())
    for ids_per_square in ids_per_square.values():
        curr_size = len(ids_per_square)
        for id in ids_per_square:
            counts_per_id[id].append(curr_size)

    for id, ids in counts_per_id.items():
        has_dupes = False
        for c in ids:
            has_dupes = has_dupes or c > 1
        if not has_dupes:
            return id


if __name__ == '__main__':
    lines = []
    for line in fileinput.input():
        lines += [line.strip()]
    print(cover(parse(lines)))


class Test032(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(
            parse(['#123 @ 3,2: 5x4']),
            [Claim(123, 3, 2, 5, 4)])

    def test_cover(self):
        self.assertEqual(
            cover([
                Claim(1, 1, 3, 4, 4),
                Claim(2, 3, 1, 4, 4),
                Claim(3, 5, 5, 2, 2)
            ]),
            3
        )
