# -*- coding: utf-8 -*-

from __future__ import unicode_literals


from search import lithuanian


def test_name_abbreviations():
    assert lithuanian.name_abbreviations('', abbr_last_name=True) == []
    assert lithuanian.name_abbreviations('Simono Stanevičiaus gatvė', abbr_last_name=True) == [
        'Simono Stanevičiaus gatvė',
        'S. Stanevičiaus gatvė',
        'Simono S. gatvė',
        'S. S. gatvė',
    ]
