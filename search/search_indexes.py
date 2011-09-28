# -*- coding: utf-8 -*-

import haystack.indexes as indexes
from haystack import site
from unidecode import unidecode
from django.db.models import Q

from search.models import Institution, Representative, Location
from search import lithuanian


def join_text(xs):
    """Joins a list of strings using newline as separator and also
    adds transliterated versions of said strings (where they differ
    from the originals).

    Useful for preparing context for indexing.
    """
    words = set()
    for x in xs:
        words.update(x.split(' '))
        words.update(unidecode(x).split(' '))
    return u' '.join(words)


class InstitutionIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True)
    auto = indexes.EdgeNgramField(model_attr='name')

    title = indexes.CharField(model_attr='name', indexed=False)
    subtitle = indexes.CharField(indexed=False)
    url = indexes.CharField(model_attr='get_absolute_url', indexed=False)

    def prepare_text(self, obj):
        return join_text([obj.name] +
                         lithuanian.nominative_names(obj.name))

    def prepare_auto(self, obj):
        return join_text([obj.name, obj.kind.name])

    def prepare_subtitle(self, obj):
        return obj.kind.name

    def index_queryset(self):
        return Institution.objects.exclude(slug='')


site.register(Institution, InstitutionIndex)


class RepresentativeIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True)
    auto = indexes.EdgeNgramField(model_attr='name')

    title = indexes.CharField(model_attr='name', indexed=False)
    subtitle = indexes.CharField(indexed=False)
    url = indexes.CharField(model_attr='get_absolute_url', indexed=False)

    def prepare_text(self, obj):
        name_variants = lithuanian.name_abbreviations(obj.name)
        return join_text([obj.kind.name,
                          obj.institution.name] +
                         name_variants)

    def prepare_auto(self, obj):
        return join_text([obj.name, obj.kind.name])

    def prepare_subtitle(self, obj):
        return u'{}, {}'.format(obj.kind.name, obj.institution.name)

    def index_queryset(self):
        return Representative.objects.exclude(slug='')


site.register(Representative, RepresentativeIndex)


class LocationIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True)
    auto = indexes.EdgeNgramField()
    numbered = indexes.BooleanField(indexed=True)

    title = indexes.CharField(indexed=False)
    subtitle = indexes.CharField(indexed=False)
    url = indexes.CharField(model_attr='get_absolute_url', indexed=False)

    def prepare_text(self, obj):
        items = ([obj.elderate,
                  obj.city] +
                 lithuanian.nominative_names(obj.city) +
                 lithuanian.nominative_names(obj.elderate) +
                 lithuanian.street_abbreviations(obj.street))

        if obj.street == '':
            # Only use municipality for searching if street is
            # empty. This improves search accuracy with the assumption
            # that there aren't cases of locations with same street
            # and city names but different municipalities.
            items += ([obj.municipality] +
                      lithuanian.nominative_names(obj.municipality))

        return join_text(items)

    def prepare_auto(self, obj):
        return join_text([obj.street, obj.city, obj.elderate])

    def prepare_numbered(self, obj):
        return obj.street != ''

    def prepare_title(self, obj):
        return ', '.join(x
                         for x in [obj.street, obj.city]
                         if x)

    def prepare_subtitle(self, obj):
        return ', '.join(x
                         for x in [obj.elderate, obj.municipality]
                         if x)

    def index_queryset(self):
        return Location.objects.exclude(slug='').exclude(
            Q(street='') & Q(city=''))

site.register(Location, LocationIndex)
