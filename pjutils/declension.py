#!/usr/bin/env python
# -*- coding: utf-8 -*-

class DeclensionLt():
    
    def kilm(self, vard):
        vard_no_end = vard[:-2]
        vard_end = [u'as', u'ai', u'is', u'us', u'ės', u'ė', u'a', u'ys']
        kilm_end = [u'o', u'ų', u'io', u'aus', u'ių', u'ės', u'os', u'ių']
        for gal in range(len(vard_end)):
            if vard[-2:]==vard_end[gal]:
                result = vard_no_end + kilm_end[gal]
        return result

    def month(self, month_no):
        months = ['Sausio', 'Vasario', 'Kovo', 'Balandžio', 'Gegužės', 'Birželio',
                  'Liepos', 'Rugpjūčio', 'Rugsėjo', 'Spalio', 'Lapkričio', 'Gruodžio']
        return months[month_no-1]

    def sauksm(self, vard):
        vard_no_end = vard[:-2]
        result = vard
        vard_end = [u'as', u'is', u'us', u'ė', u'a', u'ys']
        sauksm_end = [u'ai', u'i', u'au', u'e', u'a', u'y']
        for gal in range(len(vard_end)):
            if vard[-2:]==vard_end[gal]:
                result = vard_no_end + sauksm_end[gal]
        return result
