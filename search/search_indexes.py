# -*- coding: utf-8 -*-

import haystack.indexes as indexes
from haystack import site
from unidecode import unidecode

from search.models import Institution, Representative, Location
from search import lithuanian


def join_text(xs):
    """Joins a list of strings using newline as separator and also
    adds transliterated versions of said strings (where they differ
    from the originals).

    Useful for preparing context for indexing.
    """
    return u' '.join(set(xs + [unidecode(x) for x in xs]))


def join_auto(xs):
    return unidecode(u' '.join(xs)).strip()


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
        return join_auto([obj.name, obj.kind.name])

    def prepare_subtitle(self, obj):
        return obj.kind.name

    def index_queryset(self):
        return Representative.objects.filter(kind__active=True)


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
        return join_auto([obj.name, obj.kind.name])

    def prepare_subtitle(self, obj):
        return u'{}, {}'.format(obj.kind.name, obj.institution.name)

    def index_queryset(self):
        return Representative.objects.filter(kind__active=True)


site.register(Representative, RepresentativeIndex)


class LocationIndex(indexes.SearchIndex):
    text = indexes.CharField(document=True)
    auto = indexes.EdgeNgramField()

    title = indexes.CharField(indexed=False)
    subtitle = indexes.CharField(indexed=False)
    url = indexes.CharField(model_attr='get_absolute_url', indexed=False)

    def prepare_text(self, obj):
        return join_text(
            [obj.municipality,
             obj.elderate,
             obj.city] +
            lithuanian.nominative_names(obj.city) +
            lithuanian.nominative_names(obj.elderate) +
            lithuanian.nominative_names(obj.municipality) +
            lithuanian.street_abbreviations(obj.street)
        )

    def prepare_auto(self, obj):
        return join_auto([obj.street, obj.city, obj.elderate])

    def prepare_title(self, obj):
        return ', '.join(x
                         for x in [obj.street, obj.city]
                         if x)

    def prepare_subtitle(self, obj):
        return ', '.join(x
                         for x in [obj.elderate, obj.municipality]
                         if x)

site.register(Location, LocationIndex)
