import fileinput
from typing import List
import unittest


def process(polymer: str) -> int:
    def get_next_idx(curr_idx: int) -> int:
        next_idx = curr_idx + 1
        while next_idx < len(bitmap) and not bitmap[next_idx]:
            next_idx += 1

        if next_idx == len(bitmap):
            return None
        else:
            return next_idx

    def get_len() -> int:
        return len([x for x in bitmap if x])

    bitmap = [True] * len(polymer)

    change_made = True
    while change_made and get_len() > 0:
        change_made = False
        curr_idx = get_next_idx(-1)
        next_idx = get_next_idx(curr_idx)
        while next_idx is not None:
            curr_unit = polymer[curr_idx]
            next_unit = polymer[next_idx]
            if curr_unit != next_unit and curr_unit.upper() == next_unit.upper():
                bitmap[curr_idx] = False
                bitmap[next_idx] = False

                change_made = True

                break

            curr_idx = next_idx
            next_idx = get_next_idx(curr_idx)

    return get_len()


if __name__ == '__main__':
    lines = []
    for line in fileinput.input():
        lines += [line.strip()]

    print(process(lines[0]))


class Test051(unittest.TestCase):
    def test_process_1(self):
        self.assertEqual(
            process('aA'),
            0
        )

    def test_process_2(self):
        self.assertEqual(
            process('abBA'),
            0
        )

    def test_process_3(self):
        self.assertEqual(
            process('abAB'),
            4
        )

    def test_process_4(self):
        self.assertEqual(
            process('aabAAB'),
            6
        )

    def test_process_5(self):
        self.assertEqual(
            process('dabAcCaCBAcCcaDA'),
            10
        )
