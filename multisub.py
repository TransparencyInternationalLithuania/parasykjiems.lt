"""Functions for repeated regex replacement.
"""

import re


def multisub_all_sequential(string, re_repl_pairs):
    """Replaces all matches of every matching regex with its repl, in
    the given order.
    """
    for regex, repl in re_repl_pairs:
        string = re.sub(regex, repl, string)
    return string


def multisub_all_separate(string, re_repl_pairs):
    """Returns a set of all the strings that can be created by
    replacing the given regexes with their corresponding replacements
    in the given string.
    """
    r = set()
    for regex, repl in re_repl_pairs:
        new_string = re.sub(regex, repl, string)
        if new_string != string:
            r.add(new_string)
    return r


def multisub_one(string, re_repl_pairs):
    """Replaces all matches of the first matching regex with its repl.
    """
    for regex, repl in re_repl_pairs:
        new_string = re.sub(regex, repl, string)
        if new_string != string:
            return new_string
    return string
