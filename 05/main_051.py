import fileinput
import unittest


def process(polymer: str) -> int:
    change_made = True
    while change_made and len(polymer) > 0:
        change_made = False
        next_polymer = polymer[0]
        for i in range(1, len(polymer)):
            if (not change_made
                    and polymer[i] != polymer[i - 1]
                    and polymer[i].lower() == polymer[i - 1].lower()):
                next_polymer = next_polymer[:-1]
                change_made = True
            else:
                next_polymer += polymer[i]
        polymer = next_polymer
    return len(polymer)


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
