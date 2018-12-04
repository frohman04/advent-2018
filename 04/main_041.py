from collections import defaultdict
import datetime
import fileinput
import re
from typing import List
import unittest

BASE_PARSER = re.compile(r'\[([^]]+)\] (.*)')
GUARD_PARSER = re.compile(r'Guard #([0-9]+) begins shift')


class Event(object):
    def __init__(self, time: datetime.datetime, guard_num: int):
        self._guard_num = guard_num
        self._time = time

    def get_time(self):
        return self._time

    def get_guard_num(self):
        return self._guard_num

    def __eq__(self, other):
        return (self._time == other.get_time() and
                self._guard_num == other.get_guard_num())

    def __repr__(self):
        return 'Event({}, {})'.format(self._time, self._guard_num)


class OnDuty(Event):
    def __init__(self, time: datetime.datetime, guard_num: int):
        super(OnDuty, self).__init__(time, guard_num)

    def __repr__(self):
        return 'OnDuty({}, {})'.format(self._time, self._guard_num)


class Sleep(Event):
    def __init__(self, time: datetime.datetime, guard_num: int):
        super(Sleep, self).__init__(time, guard_num)

    def __repr__(self):
        return 'Sleep({}, {})'.format(self._time, self._guard_num)


class Wake(Event):
    def __init__(self, time: datetime.datetime, guard_num: int):
        super(Wake, self).__init__(time, guard_num)

    def __repr__(self):
        return 'Wake({}, {})'.format(self._time, self._guard_num)


class Window(object):
    def __init__(self, guard_num: int, start_min: int, end_min: int):
        self.guard_num = guard_num
        self.start_min = start_min
        self.end_min = end_min

    def __eq__(self, other):
        return (self.guard_num == other.guard_num and
                self.start_min == other.start_min and
                self.end_min == other.end_min)

    def __repr__(self):
        return 'Window({}, {}, {})'.format(self.guard_num, self.start_min, self.end_min)


def parse_line(line: str, curr_guard_num: int) -> Event:
    timestamp_str, event_str = BASE_PARSER.findall(line)[0]
    timestamp = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M')
    if 'Guard' in event_str:
        return OnDuty(timestamp, int(GUARD_PARSER.findall(event_str)[0]))
    elif event_str == 'falls asleep':
        return Sleep(timestamp, curr_guard_num)
    elif event_str == 'wakes up':
        return Wake(timestamp, curr_guard_num)


def parse(lines: List[str]) -> List[Event]:
    curr_guard_num = None
    events = []
    for line in lines:
        event = parse_line(line, curr_guard_num)
        events.append(event)
        if isinstance(event, OnDuty):
            curr_guard_num = event.get_guard_num()
    return events


def build_windows(events: List[Event]) -> List[Window]:
    guards = {}
    windows = []
    for event in events:
        if isinstance(event, Sleep):
            guards[event.get_guard_num()] = event.get_time().minute
        elif isinstance(event, Wake):
            windows.append(Window(
                event.get_guard_num(),
                guards[event.get_guard_num()],
                event.get_time().minute))
            del guards[event.get_guard_num()]
    return windows


if __name__ == '__main__':
    lines = []
    for line in fileinput.input():
        lines += [line.strip()]
    print(parse(lines))


class Test041(unittest.TestCase):
    def test_parse_line_guard_init(self):
        self.assertEqual(
            parse_line('[1518-11-01 00:00] Guard #10 begins shift', None),
            OnDuty(datetime.datetime(1518, 11, 1, 0, 0), 10))

    def test_parse_line_guard_subsequent(self):
        self.assertEqual(
            parse_line('[1518-11-01 00:00] Guard #10 begins shift', 5),
            OnDuty(datetime.datetime(1518, 11, 1, 0, 0), 10))

    def test_parse_line_sleep(self):
        self.assertEqual(
            parse_line('[1518-11-01 00:05] falls asleep', 10),
            Sleep(datetime.datetime(1518, 11, 1, 0, 5), 10))

    def test_parse_line_wake(self):
        self.assertEqual(
            parse_line('[1518-11-01 00:25] wakes up', 10),
            Wake(datetime.datetime(1518, 11, 1, 0, 25), 10))

    def test_parse(self):
        self.assertEqual(
            parse([
                '[1518-11-01 00:00] Guard #10 begins shift',
                '[1518-11-01 00:05] falls asleep',
                '[1518-11-01 00:25] wakes up',
                '[1518-11-01 23:58] Guard #99 begins shift',
                '[1518-11-02 00:40] falls asleep',
                '[1518-11-02 00:50] wakes up'
            ]),
            [
                OnDuty(datetime.datetime(1518, 11, 1, 0, 0), 10),
                Sleep(datetime.datetime(1518, 11, 1, 0, 5), 10),
                Wake(datetime.datetime(1518, 11, 1, 0, 25), 10),
                OnDuty(datetime.datetime(1518, 11, 1, 23, 58), 99),
                Sleep(datetime.datetime(1518, 11, 2, 0, 40), 99),
                Wake(datetime.datetime(1518, 11, 2, 0, 50), 99)
            ]
        )

    def test_build_windows(self):
        self.assertEqual(
            build_windows([
                OnDuty(datetime.datetime(1518, 11, 1, 0, 0), 10),
                Sleep(datetime.datetime(1518, 11, 1, 0, 5), 10),
                Wake(datetime.datetime(1518, 11, 1, 0, 25), 10),
                OnDuty(datetime.datetime(1518, 11, 1, 23, 58), 99),
                Sleep(datetime.datetime(1518, 11, 2, 0, 40), 99),
                Wake(datetime.datetime(1518, 11, 2, 0, 50), 99)
            ]),
            [
                Window(10, 5, 25),
                Window(99, 40, 50)
            ]
        )
