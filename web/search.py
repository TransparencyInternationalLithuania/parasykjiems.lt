from web.models import Representative, Territory, Institution


def find_territories(municipality=None, city=None, street=None):
    ts = Territory.objects.all()
    if municipality: ts = ts.filter(municipality__icontains=municipality)
    if city: ts = ts.filter(city__icontains=city)
    if street: ts = ts.filter(street__icontains=street)
    return ts


def find_representatives(query):
    return Representative.objects.filter(name__icontains=query)


def find_institutions(query):
    return Institution.objects.filter(name__icontains=query)


def find_anything(query):
    return (
        list(find_institutions(query)) +
        list(find_representatives(query))
    )
