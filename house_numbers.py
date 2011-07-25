import re


def _const_True(x):
    return True


def _is_even(x):
    return x % 2 == 0


def _is_odd(x):
    return x % 2 == 1


_RANGE_CHECKS = {
    'all': _const_True,
    'even': _is_even,
    'odd': _is_odd,
}


_INTERVAL_RE = re.compile(r'(\d+)-(\d+) (all|even|odd)')
_LEFT_INTERVAL_RE = re.compile(r'(\d+)- (all|even|odd)')
_SINGLE_RE = re.compile(r'(\d+\w?)')


class HouseNumberSet:
    """An object which parses a house number range definition string,
    like '3-15 odd, 4-10 even, 10A', and allows for easy checking if a
    house number (represented as a string, because it can contains a
    letter) belongs to any of those intervals.
    """
    def __init__(self, string):
        self.numbers = set()
        self.string = string

        # Intervals are stored as predicate functions.
        self.intervals = []

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
        check = _RANGE_CHECKS[kind]

        def interval(x):
            return check(x) and left <= x <= right

        self.intervals.append(interval)

    def add_left_interval(self, left, right, kind):
        left = int(left)
        right = int(right)
        check = _RANGE_CHECKS[kind]

        def left_interval(x):
            return check(x) and left <= x

        self.intervals.append(left_interval)

    def add_single(self, number):
        self.numbers.add(number)


## A map of Territory ids to corresponding HouseNumberSets
_COMPILED_HOUSE_NUMBERS = {}


def get_house_number_set(territory):
    """Returns the HouseNumberSet of this Territory. Caches them in
    _COMPILED_HOUSE_NUMBERS.
    """
    territory_id = territory.id
    if territory_id in _COMPILED_HOUSE_NUMBERS:
        return _COMPILED_HOUSE_NUMBERS[territory_id]
    else:
        hnset = HouseNumberSet(territory.numbers)
        _COMPILED_HOUSE_NUMBERS[territory_id] = hnset
        return hnset


def territory_contains(territory, house_number):
    return house_number in get_house_number_set(territory)
