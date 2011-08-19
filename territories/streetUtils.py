from django.db.models.query_utils import Q
from territories.ltPrefixes import extractStreetEndingForm

def changeDoubleWordStreetToDot(street):
    if street == u"":
        return street
    ending = extractStreetEndingForm(street)
    str = street
    if ending is not None:
        str = street.replace(ending, u"").strip()

    spl = str.split(u" ")
    if len(spl) == 1:
        return street

    final =  u" ".join(spl[1:])
    if ending is None:
        return final
    return "%s %s" % (final, ending)

def cityNameIsGenitive(municipality, city_genitive, street):
    """ given municipality, city name in genitive, and street
    return city name in nominative. This is only for Lithuanian data"""

    streetFilters = None
    if street is not None and street !="":
        streetFilters = Q(**{"street__icontains": street})
    cityFilters = Q(**{"city_genitive__icontains": city_genitive})
    municipalityFilters = Q(**{"municipality__icontains": municipality})

    if streetFilters != None:
        finalQuery = municipalityFilters & cityFilters & streetFilters
    else:
        finalQuery = municipalityFilters & cityFilters

    query = LithuanianStreetIndexes.objects.filter(finalQuery).order_by('street')[0:1]
    total= len(query)
    return total > 0

def getCityNominative(municipality, city_genitive, street):
    """ given municipality, city name in genitive, and street
    return city name in nominative. This is only for Lithuanian data"""

    streetFilters = None
    if street is not None and street !="":
        streetFilters = Q(**{"street__icontains": street})
    cityFilters = Q(**{"city_genitive__icontains": city_genitive})
    municipalityFilters = Q(**{"municipality__icontains": municipality})

    if streetFilters != None:
        finalQuery = municipalityFilters & cityFilters & streetFilters
    else:
        finalQuery = municipalityFilters & cityFilters

    query = LithuanianStreetIndexes.objects.filter(finalQuery).order_by('street')[0:1]
    for q in query:
        return q.city
    return None

def getCityGenitive(municipality, city, street):
    """ given municipality, city name in nominative, and street
    returned city name in genitive. This is only for Lithuanian data"""

    streetFilters = None
    if street is not None and street !="":
        streetFilters = Q(**{"street__icontains": street})
    cityFilters = Q(**{"city__icontains": city})
    municipalityFilters = Q(**{"municipality__icontains": municipality})

    if streetFilters != None:
        finalQuery = municipalityFilters & cityFilters & streetFilters
    else:
        finalQuery = municipalityFilters & cityFilters

    query = LithuanianStreetIndexes.objects.filter(finalQuery).order_by('street')[0:1]
    for q in query:
        return q.city_genitive
    return None
