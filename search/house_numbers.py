import re


def _const_True(x):
    return True


def _is_even(x):
    return x % 2 == 0


def _is_odd(x):
    return x % 2 == 1


_RANGE_CHECKS = {
    '': _const_True,
    ' even': _is_even,
    ' odd': _is_odd,
}


_INTERVAL_RE = re.compile(r'^(\d+)-(\d+)(| even| odd)$')
_LEFT_INTERVAL_RE = re.compile(r'^(\d+)-(| even| odd)$')
_SINGLE_RE = re.compile(r'^(\d+\w?)$')


class HouseNumberSet:
    """Given a house number range definition string, allows for easy
    checking for house number membership in that range.

    A string can contain zero or more items like:

    (1) 'X-Y' - a range of numbers from X to Y, inclusive. X and Y are
    numbers.

    (2) 'X-Y odd' and 'X-Y even' - like (1), but only includes odd or
    even numbers respectively.

    (3) 'X-', 'X- odd', 'X- even' - like (1) and (2), but doesn't have
    an upper limit.

    (4) 'X' - denotes a single house number. May also contain a
    letter.

    A string with no items means that it contains all house numbers.

    >>> s = HouseNumberSet('3-13 odd, 6-16 even, 10a, 18A, 30-40, 50- odd')
    >>> 1 in s
    False
    >>> 3 in s
    True
    >>> '3a' in s
    False
    >>> 4 in s
    False
    >>> 5 in s
    True
    >>> 6 in s
    True

    >>> '10A' in s
    True
    >>> '10a' in s
    True
    >>> 18 in s
    False
    >>> '18a' in s
    True

    >>> 30 in s
    True
    >>> 31 in s
    True

    >>> 60 in s
    False
    >>> 61 in s
    True

    >>> s = HouseNumberSet('')
    >>> '123a' in s
    True
    """

    def __init__(self, string):
        self.string = string

        if string == '':
            # An empty string is a wildcard.
            self.universal = True
        else:
            self.universal = False
            self.numbers = set()
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

                raise ValueError(
                    'Bad house number definition string item "{}" in "{}".'
                    .format(item, string))

    def __unicode__(self):
        return self.string

    def __contains__(self, x):
        if self.universal:
            return True
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

    def add_left_interval(self, left, kind):
        left = int(left)
        check = _RANGE_CHECKS[kind]

        def left_interval(x):
            return check(x) and left <= x

        self.intervals.append(left_interval)

    def add_single(self, number):
        self.numbers.add(number.upper())


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
    """Checks if a territory contains a house number.

    >>> from web.models import Location, Territory
    >>> t = Territory(location=Location('a', 'b'), numbers='10-14 even')
    >>> territory_contains(t, 1)
    False
    >>> territory_contains(t, 11)
    False
    >>> territory_contains(t, 12)
    True
    """
    return house_number in get_house_number_set(territory)
