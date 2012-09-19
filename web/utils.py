# -*- coding: utf-8 -*-
import re


_MULTIPLE_SPACES = re.compile(r'\s\s+')


def summary(s, length=80):
    short = s[:length]
    if short != s:
        short += u'…'
    return _MULTIPLE_SPACES.sub(' ', short.replace('\n', ' '))
