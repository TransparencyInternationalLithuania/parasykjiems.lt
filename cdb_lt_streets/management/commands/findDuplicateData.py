#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cdb_lt_seniunaitija.models import SeniunaitijaStreet
from cdb_lt_streets.streetUtils import getCityNominative
from django.core.management.base import BaseCommand
from pjweb.views import findSeniunaitijaMembers

class Command(BaseCommand):
    args = '<>'
    help = ''

    def handle(self, *args, **options):


        for streetObject in SeniunaitijaStreet.objects.all():
            municipality = streetObject.municipality
            city = streetObject.city
            house_number = streetObject.numberFrom
            city_genitive = city
            street = streetObject.street
            city = getCityNominative(municipality=municipality, city_genitive=city_genitive, street= street)


            municipality = u"Šilalės rajono"
            city_genitive = u"Kalniškių kaimas"
            street = None
            house_number = None
            city = None

            additionalKeys = {"city_genitive" : city_genitive}
            members = findSeniunaitijaMembers(municipality, city, street, house_number, **additionalKeys)

            if house_number is None:
                house_number = ""
            if street is None:
                street = ""
            print "adress: %s %s %s %s" % (street, house_number, city_genitive, municipality)
            total = len(members)
            print "%s member" % total

            for m in members:
                print "%s %s" % (m.name, m.surname)

            print ""
        
