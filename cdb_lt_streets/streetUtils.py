from cdb_lt_streets.models import LithuanianStreetIndexes
from django.db.models.query_utils import Q

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
