import re

def stringIsIn(str, values):
    """ brute force IN operation.  should use regex later
    """
    if str is None:
        return False
    regex = []
    str = str.lower()
    v = [v.lower() for v in values]
    for v in values:
        if str == v:
            return True
        s = u"\b%s\b" % v
        search = re.compile(s, re.IGNORECASE)
        r = search.search(str)
        if r is not None:
            return True

    """regex.append(s)
    regex = u"|".join(regex)
    search = re.compile(regex, re.IGNORECASE)
    r = search.search(str)
    return r is not None"""
    return False
"""
    str = str.lower()
    values = [v.lower() for v in values]
    for v in values:
        if str.find(v) >= 0:
            return True
    return False"""