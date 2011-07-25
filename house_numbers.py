import re

_INTERVAL_RE = re.compile(r'(\d+)-(\d+) (all|even|odd)')
_LEFT_INTERVAL_RE = re.compile(r'(\d+)- (all|even|odd)')
_SINGLE_RE = re.compile(r'(\d+\w?)')

_ALL, _EVEN, _ODD = range(3)


class HouseNumberSet:
    """An object which parses a house number range definition string,
    like '3-15 odd, 4-10 even, 10A', and allows for easy checking if a
    house number (represented as a string, because it can contains a
    letter) belongs to any of those intervals.
    """
    def __init__(self, string):
        self.numbers = set()
        self.intervals = []
        self.string = string
        for item in string.split(','):
            item = item.strip()

            m = _INTERVAL_RE.match(item)
            if m:
                self.add_interval(m.group(1), m.group(2), m.group(3))
                continue

            m = _LEFT_INTERVAL_RE.match(item)
            if m:
                self.add_left_interval(m.group(1), m.group(2))
                continue

            m = _SINGLE_RE.match(item)
            if m:
                self.add_single(m.group(1))
                continue

    def __unicode__(self):
        return self.string

    def __contains__(self, x):
        xs = str(x)
        if xs.upper() in self.numbers:
            return True

        try:
            xi = int(x)
            for interval_fn in self.intervals:
                if interval_fn(xi):
                    return True
            return False
        except ValueError:
            return False

    def add_interval(self, left, right, kind):
        left = int(left)
        right = int(right)
        if kind == 'all':
            def allin(x):
                return left <= x <= right
            self.intervals.append(allin)
        elif kind == 'even':
            def evenin(x):
                return (x % 2 == 0) and (left <= x <= right)
            self.intervals.append(evenin)
        else:
            def oddin(x):
                return (x % 2 == 1) and (left <= x <= right)
            self.intervals.append(oddin)

    def add_left_interval(self, left, kind):
        if kind == 'all':
            def allin(x):
                return left <= x
            self.intervals.append(allin)
        elif kind == 'even':
            def evenin(x):
                return (x % 2 == 0) and (left <= x)
            self.intervals.append(evenin)
        else:
            def oddin(x):
                return (x % 2 == 1) and (left <= x)
            self.intervals.append(oddin)

    def add_single(self, number):
        self.numbers.add(number)


## A map of Territory ids to corresponding HouseNumberSets
_COMPILED_HOUSE_NUMBERS = {}


def get_house_number_set(territory):
    """Returns the HouseNumberSet of this Territory. Caches them in
    _COMPILED_HOUSE_NUMBERS.
    """
    id = territory.id
    if id in _COMPILED_HOUSE_NUMBERS:
        return _COMPILED_HOUSE_NUMBERS[id]
    else:
        hnset = HouseNumberSet(territory.numbers)
        _COMPILED_HOUSE_NUMBERS[id] = hnset
        return hnset


def territory_contains(territory, house_number):
    return house_number in get_house_number_set(territory)
