# -*- coding: utf-8 -*-

from haystack import indexes
from unidecode import unidecode

from search.models import Institution, Representative, Location
from search import lithuanian


def join_text(xs):
    """Joins a list of strings using newline as separator and also
    adds transliterated versions of said strings (where they differ
    from the originals).

    Useful for preparing context for indexing.
    """
    lines = set(xs)
    lines.update(unidecode(x) for x in xs)
    return u'\n'.join(lines)


MUNICIPALITY_POPULATIONS = {
    u'Vilniaus miesto savivaldybė': 554409,
    u'Kauno miesto savivaldybė': 358111,
    u'Klaipėdos miesto savivaldybė': 185936,
    u'Šiaulių miesto savivaldybė': 128397,
    u'Panevėžio miesto savivaldybė': 114582,
    u'Vilniaus rajono savivaldybė': 94171,
    u'Kauno rajono savivaldybė': 85721,
    u'Marijampolės savivaldybė': 69297,
    u'Alytaus miesto savivaldybė': 68835,
    u'Mažeikių rajono savivaldybė': 65554,
    u'Kėdainių rajono savivaldybė': 63563,
    u'Telšių rajono savivaldybė': 55231,
    u'Šilutės rajono savivaldybė': 53373,
    u'Jonavos rajono savivaldybė': 51941,
    u'Tauragės rajono savivaldybė': 51049,
    u'Šiaulių rajono savivaldybė': 50480,
    u'Radviliškio rajono savivaldybė': 49705,
    u'Klaipėdos rajono savivaldybė': 49295,
    u'Vilkaviškio rajono savivaldybė': 48380,
    u'Utenos rajono savivaldybė': 48378,
    u'Ukmergės rajono savivaldybė': 46303,
    u'Kretingos rajono savivaldybė': 45956,
    u'Plungės rajono savivaldybė': 43580,
    u'Panevėžio rajono savivaldybė': 43190,
    u'Raseinių rajono savivaldybė': 42377,
    u'Rokiškio rajono savivaldybė': 39451,
    u'Kelmės rajono savivaldybė': 38615,
    u'Šalčininkų rajono savivaldybė': 37852,
    u'Šakių rajono savivaldybė': 36805,
    u'Trakų rajono savivaldybė': 36429,
    u'Kaišiadorių rajono savivaldybė': 36290,
    u'Jurbarko rajono savivaldybė': 35622,
    u'Prienų rajono savivaldybė': 34025,
    u'Biržų rajono savivaldybė': 33491,
    u'Pasvalio rajono savivaldybė': 32961,
    u'Anykščių rajono savivaldybė': 32629,
    u'Alytaus rajono savivaldybė': 31420,
    u'Švenčionių rajono savivaldybė': 31130,
    u'Šilalės rajono savivaldybė': 30431,
    u'Joniškio rajono savivaldybė': 30429,
    u'Varėnos rajono savivaldybė': 28960,
    u'Visagino savivaldybė': 28576,
    u'Akmenės rajono savivaldybė': 28204,
    u'Elektrėnų savivaldybė': 28093,
    u'Pakruojo rajono savivaldybė': 27883,
    u'Lazdijų rajono savivaldybė': 25233,
    u'Druskininkų savivaldybė': 24507,
    u'Skuodo rajono savivaldybė': 24148,
    u'Molėtų rajono savivaldybė': 23539,
    u'Kupiškio rajono savivaldybė': 23444,
    u'Zarasų rajono savivaldybė': 20997,
    u'Ignalinos rajono savivaldybė': 20624,
    u'Širvintų rajono savivaldybė': 19367,
    u'Palangos miesto savivaldybė': 17632,
    u'Kazlų Rūdos savivaldybė': 14615,
    u'Kalvarijos savivaldybė': 13490,
    u'Pagėgių savivaldybė': 11577,
    u'Rietavo savivaldybė': 10208,
    u'Birštono savivaldybė': 5256,
    u'Neringos savivaldybė': 3132,
}

MUNICIPALITY_MAX_POPULATION = max(MUNICIPALITY_POPULATIONS.values())
MUNICIPALITY_MIN_POPULATION = min(MUNICIPALITY_POPULATIONS.values())


def get_municipality_boost(municipality):
    return (float(MUNICIPALITY_POPULATIONS[municipality] -
                  MUNICIPALITY_MIN_POPULATION) /
            (MUNICIPALITY_MAX_POPULATION - MUNICIPALITY_MIN_POPULATION))


def get_institution_boost(name):
    boost = 2
    if u'savivaldybė' in name:
        boost -= 1
        for municipality, pop in MUNICIPALITY_POPULATIONS.items():
            if municipality in name:
                boost += get_municipality_boost(municipality)
        if u'seniūnija' in name:
            boost -= 1
        if u'kaimo' in name:
            boost -= 1
    return boost


class InstitutionIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    auto = indexes.EdgeNgramField(model_attr='name')

    title = indexes.CharField(model_attr='name', indexed=False)
    subtitle = indexes.CharField(indexed=False)
    url = indexes.CharField(model_attr='get_absolute_url', indexed=False)

    def get_model(self):
        return Institution

    def prepare_text(self, obj):
        return join_text([obj.name] +
                         lithuanian.nominative_names(obj.name))

    def prepare_auto(self, obj):
        return self.prepare_text(obj)

    def prepare_subtitle(self, obj):
        return obj.kind.name

    def prepare(self, obj):
        data = super(InstitutionIndex, self).prepare(obj)
        data['boost'] = 10 + get_institution_boost(obj.name)
        return data

    def index_queryset(self, using=None):
        return Institution.objects.exclude(slug='')


class RepresentativeIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    auto = indexes.EdgeNgramField(model_attr='name')

    title = indexes.CharField(model_attr='name', indexed=False)
    subtitle = indexes.CharField(indexed=False)
    url = indexes.CharField(model_attr='get_absolute_url', indexed=False)

    def get_model(self):
        return Representative

    def prepare_text(self, obj):
        name_variants = lithuanian.name_abbreviations(obj.name, abbr_last_name=True)
        return join_text([obj.kind.name,
                          obj.institution.name] +
                         name_variants)

    def prepare_auto(self, obj):
        return self.prepare_text(obj)

    def prepare_subtitle(self, obj):
        return u'{}, {}'.format(obj.kind.name, obj.institution.name)

    def prepare(self, obj):
        data = super(RepresentativeIndex, self).prepare(obj)
        data['boost'] = 5 + get_institution_boost(obj.institution.name)
        return data

    def index_queryset(self, using=None):
        return Representative.objects.exclude(slug='')


class LocationIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True)
    auto = indexes.EdgeNgramField()
    numbered = indexes.BooleanField(indexed=False)

    title = indexes.CharField(indexed=False)
    subtitle = indexes.CharField(indexed=False)
    url = indexes.CharField(model_attr='get_absolute_url', indexed=False)

    def get_model(self):
        return Location

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
        return self.prepare_text(obj)

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

    def prepare(self, obj):
        data = super(LocationIndex, self).prepare(obj)
        data['boost'] = 1 + get_municipality_boost(obj.municipality)
        if obj.street == None:
            data['boost'] -= 0.1
        return data
