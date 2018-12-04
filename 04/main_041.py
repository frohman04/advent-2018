from collections import defaultdict
import datetime
import fileinput
import re
from typing import List
import unittest

BASE_PARSER = re.compile(r'\[([^]]+)\] (.*)')
GUARD_PARSER = re.compile(r'Guard #([0-9]+) begins shift')


class RawEvent(object):
    def __init__(self, time: datetime.datetime, desc: str):
        self.time = time
        self.desc = desc

    def __eq__(self, other):
        return (self.time == other.time and
                self.desc == other.desc)

    def __repr__(self):
        return 'RawEvent({}, {})'.format(self.time, self.desc)


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


def parse_line_raw(line: str) -> RawEvent:
    timestamp_str, event_str = BASE_PARSER.findall(line)[0]
    timestamp = datetime.datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M')
    return RawEvent(timestamp, event_str)


def parse_line(raw_event: RawEvent, curr_guard_num: int) -> Event:
    if 'Guard' in raw_event.desc:
        return OnDuty(raw_event.time, int(GUARD_PARSER.findall(raw_event.desc)[0]))
    elif raw_event.desc == 'falls asleep':
        return Sleep(raw_event.time, curr_guard_num)
    elif raw_event.desc == 'wakes up':
        return Wake(raw_event.time, curr_guard_num)


def parse(lines: List[str]) -> List[Event]:
    raw_events = []
    for line in lines:
        raw_event = parse_line_raw(line)
        raw_events.append(raw_event)

    raw_events = sorted(raw_events, key=lambda x: x.time)

    curr_guard_num = None
    events = []
    for raw_event in raw_events:
        event = parse_line(raw_event, curr_guard_num)
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


def find_sleepiest_guard(windows: List[Window]) -> int:
    guards = defaultdict(lambda: 0)
    for window in windows:
        guards[window.guard_num] += (window.end_min - window.start_min)

    sleepiest = -1
    most_sleep = -1
    for guard, sleep_time in guards.items():
        if sleep_time > most_sleep:
            most_sleep = sleep_time
            sleepiest = guard

    return sleepiest


def find_sleepiest_minute(windows: List[Window], guard_num: int) -> int:
    minutes = [0] * 60
    for window in windows:
        if window.guard_num == guard_num:
            for i in range(window.start_min, window.end_min):
                minutes[i] += 1

    freq_minute = -1
    times_slept = -1
    for i in range(len(minutes)):
        if minutes[i] > times_slept:
            times_slept = minutes[i]
            freq_minute = i

    return freq_minute


def process(lines: List[str]) -> int:
    events = parse(lines)
    windows = build_windows(events)
    sleepiest_guard = find_sleepiest_guard(windows)
    sleepiest_minute = find_sleepiest_minute(windows, sleepiest_guard)
    return sleepiest_guard * sleepiest_minute


if __name__ == '__main__':
    lines = []
    for line in fileinput.input():
        lines += [line.strip()]

    print(process(lines))


class Test041(unittest.TestCase):
    def test_parse_line_raw(self):
        self.assertEqual(
            parse_line_raw('[1518-11-01 00:00] Guard #10 begins shift'),
            RawEvent(datetime.datetime(1518, 11, 1, 0, 0), 'Guard #10 begins shift')
        )

    def test_parse_line__guard_init(self):
        self.assertEqual(
            parse_line(
                RawEvent(datetime.datetime(1518, 11, 1, 0, 0), 'Guard #10 begins shift'),
                None),
            OnDuty(datetime.datetime(1518, 11, 1, 0, 0), 10))

    def test_parse_line__guard_subsequent(self):
        self.assertEqual(
            parse_line(
                RawEvent(datetime.datetime(1518, 11, 1, 0, 0), 'Guard #10 begins shift'),
                5),
            OnDuty(datetime.datetime(1518, 11, 1, 0, 0), 10))

    def test_parse_line__sleep(self):
        self.assertEqual(
            parse_line(
                RawEvent(datetime.datetime(1518, 11, 1, 0, 5), 'falls asleep'),
                10),
            Sleep(datetime.datetime(1518, 11, 1, 0, 5), 10))

    def test_parse_line__wake(self):
        self.assertEqual(
            parse_line(
                RawEvent(datetime.datetime(1518, 11, 1, 0, 25), 'wakes up'),
                10),
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

    def test_parse__out_of_order(self):
        self.assertEqual(
            parse([
                '[1518-11-01 00:05] falls asleep',
                '[1518-11-01 23:58] Guard #99 begins shift',
                '[1518-11-01 00:00] Guard #10 begins shift',
                '[1518-11-01 00:25] wakes up',
                '[1518-11-02 00:50] wakes up',
                '[1518-11-02 00:40] falls asleep',
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

    def test_find_sleepiest_guard(self):
        self.assertEqual(
            find_sleepiest_guard([
                Window(10, 5, 25),
                Window(10, 30, 55),
                Window(99, 40, 50),
                Window(10, 24, 29),
                Window(99, 36, 46),
                Window(99, 45, 55)
            ]),
            10
        )

    def test_find_sleepiest_minute(self):
        self.assertEqual(
            find_sleepiest_minute(
                [
                    Window(10, 5, 25),
                    Window(10, 30, 55),
                    Window(99, 40, 50),
                    Window(10, 24, 29),
                    Window(99, 36, 46),
                    Window(99, 45, 55)
                ],
                10
            ),
            24
        )

    def test_process(self):
        self.assertEqual(
            process([
                '[1518-11-01 00:00] Guard #10 begins shift',
                '[1518-11-01 00:05] falls asleep',
                '[1518-11-01 00:25] wakes up',
                '[1518-11-01 00:30] falls asleep',
                '[1518-11-01 00:55] wakes up',
                '[1518-11-01 23:58] Guard #99 begins shift',
                '[1518-11-02 00:40] falls asleep',
                '[1518-11-02 00:50] wakes up',
                '[1518-11-03 00:05] Guard #10 begins shift',
                '[1518-11-03 00:24] falls asleep',
                '[1518-11-03 00:29] wakes up',
                '[1518-11-04 00:02] Guard #99 begins shift',
                '[1518-11-04 00:36] falls asleep',
                '[1518-11-04 00:46] wakes up',
                '[1518-11-05 00:03] Guard #99 begins shift',
                '[1518-11-05 00:45] falls asleep',
                '[1518-11-05 00:55] wakes up'
            ]),
            240
        )
