#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.test import TestCase
import os
from cdb_lt_seniunaitija.management.commands.importSeniunaitijaStreets import SeniunaitijaAddressExpander, ExpandedStreet

scriptPath = os.path.dirname( os.path.realpath( __file__ ) )

class TestSeniunaitijaAddressExpander(TestCase):
    parser = SeniunaitijaAddressExpander()
    def assertTuplesEqual(self, original, toTest):

        generated = list(toTest)
        both = zip(original, generated)

        for o, t in both:
            self.assertEqual(o.street, t.street)
            self.assertEqual(o.numberFrom, t.numberFrom)
            self.assertEqual(o.numberTo, t.numberTo)
            self.assertEqual(o.city, t.city)

        self.assertEqual(len(list(original)), len(generated))

    def test_Empty(self):
        original = [ExpandedStreet()]

        self.assertTuplesEqual(original, self.parser.ExpandStreet(""))
        self.assertTuplesEqual(original, self.parser.ExpandStreet(None))
        self.assertTuplesEqual(original, self.parser.ExpandStreet("    "))

    def test_WithCityAndStreets(self):
        original = [ExpandedStreet(street = u"Ateities g.", city = u"Vandžiogalos miestelis"),
                    ExpandedStreet(street = u"Kauno g.", city = u"Vandžiogalos miestelis")]
        self.assertTuplesEqual(original, self.parser.ExpandStreet(u"Vandžiogalos mstl. Ateities g., Kauno g."))



    def test_CityNamesNotInGenitive(self):
        str = [u"Baliuliai", u"Gužiai", u"Kalviškė", u"Katelninkai", u"Merionys I", u"Padvarė", u"Pamerionys", u"Sarokpolis"]
        original = [ExpandedStreet(city = city) for city in str]
        self.assertTuplesEqual(original, self.parser.ExpandStreet(u"Baliuliai, Gužiai, Kalviškė, Katelninkai, Merionys I, Padvarė, Pamerionys, Sarokpolis"))


        
    def test_HouseRanges(self):
        original = [ExpandedStreet(street = u"Vytauto g.", numberFrom = 2, numberTo = 36)]
        self.assertTuplesEqual(original, self.parser.ExpandStreet(u"Vytauto g. 2-36"))

    def test_HouseRanges_Tillinfinity(self):

       original = [ExpandedStreet(street = u"Technikos g.", numberFrom = 78, numberTo= ExpandedStreet.MaxEvenValue)]
       self.assertTuplesEqual(original, self.parser.ExpandStreet(u"Technikos g. poriniai numeriai nuo Nr. 78 iki galo"))



    def test_NoCityStreetNumbers(self):

        original = [ExpandedStreet(street = u"Žeimių g.", numberFrom = 2),
                    ExpandedStreet(street = u"Žeimių g.", numberFrom = 2),
                    ExpandedStreet(street = u"Žeimių g.", numberFrom = 4),
                    ExpandedStreet(street = u"Žeimių g.", numberFrom = 6),
                    ExpandedStreet(street = u"Žeimių g.", numberFrom = 6),]
        self.assertTuplesEqual(original, self.parser.ExpandStreet(u"Žeimių g. 2,2a,4,6,6a"))

    def test_HouseRangesWithWords(self):
        original = [ExpandedStreet(street = u"Vilniaus g.", numberFrom = 1, numberTo = 45),
                    ExpandedStreet(street = u"Vilniaus g.", numberFrom = 2, numberTo = 66),
                    ExpandedStreet(street = u"Kranto g.")]

        self.assertTuplesEqual(original, self.parser.ExpandStreet(u"Vilniaus g. neporiniai nuo Nr.1 iki Nr. 45, poriniai nuo Nr. 2 iki Nr. 66, Kranto g."))


    def test_street_g(self):
        original = [ExpandedStreet(city = u"Mankiškės k."),
                    ExpandedStreet(city = u"Palaimos k."),
                    ExpandedStreet(city = u"Tūjainių k.")]
        self.assertTuplesEqual(original, self.parser.ExpandStreet(u"Mankiškės k., Palaimos k., Tūjainių k."))

    #Vilniaus g. individualiųjų namų dalis (nuo namo Nr.1 iki Nr. 45 ir nuo Nr. 2 iki Nr. 66), Kranto g., Svajonių g., Upės g., Žeimenos g.
    #Vidiškių kaimo Melioratorių g. gyv. namai Nr.: 4, 5, 6, 9, 10, 13, 15, 7, 14, 16, 18.
    #Kretingos g. neporiniai numeriai nuo Nr. 25 iki Nr. 81, Liepojos g. poriniai numeriai nuo Nr. 2 iki Nr. 24, P. Lideikio g.

    # Kalnų g. neporiniai namai 25-27, 64, 64A, Klaipėdos g., Liepų g., Plento g., Vasario 16-os g. 1-18, 20, 22-24, Vilniaus g., Žalioji g., Žeimių g. neporiniai namai 1-7, s/b „Draugystė“, s/b „Pušaitė“
    #Valčiūnų kaimo Geležinkeliečių g. 8, 10,12,14
    #Miško g. nuo 1 iki 37 (neporiniai numeriai), nuo 10 iki 32 (poriniai numeriai), Pušų g., Taikos g., Zapyškio g., Kauno g. nuo 2 iki 18 (poriniai numeriai) ir nuo 1 iki 25 (neporiniai numeriai), Liepų g.
    #Miško g. nuo 34 iki 38A (poriniai numeriai), Kauno g. nuo 27 iki 31B (neporiniai numeriai)
    #J. Janonio g. 78 iki 112
    #Šaltinio g., J. Zikaro g.,             P. Mašioto g., J. Biliūno g. nuo 1 iki 14A
    #Europos parko al., I. Končiaus skg., Mozūrų g., Minijos g.,  Rietavo g. namų poriniai numeriai iki Nr. 28 ir namų neporiniai numeriai iki Nr. 31, Palankės g., Smilties g., J. Tumo-Vaižganto g. tik namų neporiniai numeriai iki Nr. 79, S. Nėries g. namų poriniai numeriai iki Nr. 16 ir namų neporiniai numeriai iki Nr. 11, Senamiesčio a., Sinagogų g., Telšių g. namų poriniai numeriai iki Nr. 12
    #J. Tumo-Vaižganto g. tik poriniai namų numeriai nuo Nr. 78 iki Nr. 96, V. Mačernio g. Nr. 45a ir tik neporiniai namų numeriai iki Nr. 45.

    #Užliedžių k. Nevėžio g., Trumposios g., Žemaičių g., Plento g., Krūmų g., Ledos g. 1, 3, 4, 5, 6 ir 8, Volungės g., Bivylių k., Paltiškių k., Romainių k., Kudrėnų k.








