from concurrent.futures import ProcessPoolExecutor, as_completed
import fileinput
from typing import List, Tuple
import unittest


def process_one(polymer: str, bitmap: List[bool] = None) -> int:
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

    if bitmap is None:
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


def process_one_remove(polymer: str, char: str) -> Tuple[int, str]:
    char = char[0].lower()
    bitmap = [x.lower() != char for x in polymer]
    return process_one(polymer, bitmap), char


def process(polymer: str) -> int:
    chars = set([x.lower() for x in polymer])
    min_length = len(polymer) + 1

    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = [executor.submit(process_one_remove, polymer, char) for char in chars]

        for future in as_completed(futures):
            length, char = future.result()
            print('{}: {}'.format(char, length))
            min_length = min(min_length, length)

    return min_length


if __name__ == '__main__':
    lines = []
    for line in fileinput.input():
        lines += [line.strip()]

    print(process(lines[0]))


class Test052(unittest.TestCase):
    def test_process_one_1(self):
        self.assertEqual(
            process_one('aA'),
            0
        )

    def test_process_one_2(self):
        self.assertEqual(
            process_one('abBA'),
            0
        )

    def test_process_one_3(self):
        self.assertEqual(
            process_one('abAB'),
            4
        )

    def test_proces_one_4(self):
        self.assertEqual(
            process_one('aabAAB'),
            6
        )

    def test_process_one_5(self):
        self.assertEqual(
            process_one('dabAcCaCBAcCcaDA'),
            10
        )

    def test_process_one_remove_1(self):
        self.assertEqual(
            process_one_remove('dabAcCaCBAcCcaDA', 'a'),
            6
        )

    def test_process_one_remove_2(self):
        self.assertEqual(
            process_one_remove('dabAcCaCBAcCcaDA', 'b'),
            8
        )

    def test_process_one_remove_3(self):
        self.assertEqual(
            process_one_remove('dabAcCaCBAcCcaDA', 'c'),
            4
        )

    def test_process_one_remove_4(self):
        self.assertEqual(
            process_one_remove('dabAcCaCBAcCcaDA', 'd'),
            6
        )

    def test_process(self):
        self.assertEqual(
            process('dabAcCaCBAcCcaDA'),
            4
        )
