# -*- coding: utf-8 -*-
"""Exports all data from the database into a more sensible format.

Puts results in CSV files into the export directory.
"""

import csv
import os
import sys
os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

from contactdb.models import InstitutionType, PersonPosition
from territories.models import InstitutionTerritory

if not os.path.exists('export'):
    os.mkdir('export')

def e(s):
    return s.encode('utf-8')

print 'Exporting %d InstitutionTypes.' % len(InstitutionType.objects.all()),
with open('export/institutiontypes.csv', 'wb') as f:
    sys.stdout.flush()
    w = csv.DictWriter(f,
                       ['id',
                        'name'])
    w.writeheader()
    c = 0
    for it in InstitutionType.objects.all():
        c += 1
        if c % 1000 == 0:
            print ' ... %d' % c,
            sys.stdout.flush()
        w.writerow({'id': str(it.id),
                    'name': e(it.code)})
print

print 'Exporting %d PersonPositions.' % len(PersonPosition.objects.all()),
with open('export/personpositions.csv', 'wb') as f:
    sys.stdout.flush()
    w = csv.DictWriter(f,
                       ['full_name',
                        'institution_name',
                        'institution_id',
                        'institution_type',
                        'email',
                        'contact_info'])
    w.writeheader()
    c = 0
    for p in PersonPosition.objects.all():
        c += 1
        if c % 1000 == 0:
            print ' ... %d' % c,
            sys.stdout.flush()
        contact_fields = [p.primaryPhone,
                          p.secondaryPhone,
                          p.institution.officeAddress]

        contact_info = u'\n'.join(y for x in
                                  [p.secondaryPhone,
                                   p.institution.officeAddress]
                                  for y in [unicode(x).strip()]
                                  if y != '' and y != '-')
        
        w.writerow({'full_name': e(p.person.fullName),
                    'institution_name': e(p.institution.name),
                    'institution_id': str(p.institution.id),
                    'institution_type': str(p.institution.institutionType.id),
                    'email': e(p.email),
                    'contact_info': e(contact_info)})
print

print 'Exporting %d InstitutionTerritories.' % \
      len(InstitutionTerritory.objects.all()),
with open('export/institutionterritories.csv', 'wb') as f:
    sys.stdout.flush()
    w = csv.DictWriter(f,
                       ['institution_id',
                        'municipality',
                        'eldership',
                        'city',
                        'street',
                        'number_from',
                        'number_to',
                        'number_filter',
                        'comment'])
    w.writeheader()
    c = 0
    for t in InstitutionTerritory.objects.all():
        c += 1
jhn        if c % 1000 == 0:
            print ' ... %d' % c,
            sys.stdout.flush()
        if t.numberOdd is None:
            number_filter = 'all'
        elif t.numberOdd:
            number_filter = 'odd'
        else:
            number_filter = 'even'
        w.writerow({'institution_id': str(t.institution.id),
                    'municipality': e(t.municipality),
                    'eldership': e(t.civilParish),
                    'city': e(t.city),
                    'street': e(t.street),
                    'number_from': e(t.numberFrom),
                    'number_to': e(t.numberTo),
                    'number_filter': number_filter,
                    'comment': e(t.comment)})
print
