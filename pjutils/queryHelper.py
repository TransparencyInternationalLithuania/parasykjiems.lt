from django.db.models.query_utils import Q

def getOrQuery(fieldName, fieldValues):
    streetFilters = None
    for s in fieldValues:
        q = Q(**{"%s__icontains" % fieldName: s})
        if streetFilters is None:
            streetFilters = q
        else:
            streetFilters = streetFilters | q
    return streetFilters

def getAndQuery(*args):
    """ adds all queries into one. Skips empty queries"""
    finalQuery = None
    for q in args:
        if q is None:
            continue
        if finalQuery is None:
            finalQuery = q
        else:
            finalQuery = finalQuery & q
    return finalQuery
