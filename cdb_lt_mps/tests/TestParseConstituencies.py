#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cdb_lt_mps.parseConstituencies import PollingDistrictStreetExpander, ExpandedStreet, LithuanianConstituencyParser, LithuanianConstituencyReader, AddressParser
from django.test.testcases import TestCase
import os


scriptPath = os.path.dirname( os.path.realpath( __file__ ) )

class TestLithuanianConstituencyParser(TestCase):
    parser = LithuanianConstituencyParser()

    def test_ExtractConstituencyFromConstituencyFile(self):
        Constituency = self.parser.ExtractConstituencyFromConstituencyFile("Lazdynų rinkimų apygarda Nr. 9")
        self.assertEqual("Lazdynų rinkimų apygarda", Constituency.name)
        self.assertEqual(9, Constituency.nr)

    def test_ExtractConstituencyFromMPsFile(self):
        Constituency = self.parser.ExtractConstituencyFromMPsFile(u"Naujamiesčio (Nr. 1)")
        self.assertEqual(u"Naujamiesčio", Constituency.name)
        self.assertEqual(1, Constituency.nr)


class TestPollingDistrictStreetExpander(TestCase):
    parser = PollingDistrictStreetExpander()

    def assertTuplesEqual(self, original, toTest):

        generated = list(toTest)
        both = zip(original, generated)

        for o, t in both:
            self.assertEqual(o.street, t.street)
            self.assertEqual(o.numberFrom, t.numberFrom)
            self.assertEqual(o.numberTo, t.numberTo)

        self.assertEqual(len(list(original)), len(generated))



    def test_Empty(self):
        original = [ExpandedStreet("")]

        self.assertTuplesEqual(original, self.parser.ExpandStreet(""))
        self.assertTuplesEqual(original, self.parser.ExpandStreet(None))
        self.assertTuplesEqual(original, self.parser.ExpandStreet("    "))

    def test_street_g(self):
        original = [ExpandedStreet(street = u"Mano gatvė")]
        self.assertTuplesEqual(original, self.parser.ExpandStreet("Mano g."))

    def test_street_pr(self):
        original = [ExpandedStreet(u"Baltų prospektas", 1),
                    ExpandedStreet(u"Baltų prospektas", 2)]
        self.assertTuplesEqual(original, self.parser.ExpandStreet(u"Baltų pr. Nr.1; Nr. 2"))

    def test_street_pl(self):
        original = [ExpandedStreet(u"Baltų plentas", 1),
                    ExpandedStreet(u"Baltų plentas", 2)]
        self.assertTuplesEqual(original, self.parser.ExpandStreet(u"Baltų pl. Nr.1; Nr. 2"))

    def test_street_al(self):
        original = [ExpandedStreet(u"Baltų alėja", 1), ExpandedStreet(u"Baltų alėja", 2)]
        self.assertTuplesEqual(original, self.parser.ExpandStreet(u"Baltų al. Nr.1; Nr. 2"))

    def test_SB(self):
        original = [ExpandedStreet(u"SB Dailė.", 1), ExpandedStreet(u"SB Dailė.", 2)]
        self.assertTuplesEqual(original, self.parser.ExpandStreet(u"SB Dailė. Nr.1; Nr. 2"))
        #SB „Dailė“ Nr. 1, Nr. 27, Nr. 30, Nr. 50, Nr. 52, Nr. 56



    def test_OneHouse(self):

        vec = [18, 20, 22, 24, 26, 27, 29]
        original = [ExpandedStreet(u"Respublikos gatvė", x) for x in vec]

        self.assertTuplesEqual(original, self.parser.ExpandStreet("Respublikos g. Nr. 18; Nr. 20; Nr. 22; Nr. 24; Nr. 26; Nr. 27; Nr. 29"))

    def test_OneHouse_OneContinuosRange(self):
        original = [ExpandedStreet(u"Respublikos gatvė", 1, 17)]
        self.assertTuplesEqual(original, self.parser.ExpandStreet("Respublikos g. poriniai numeriai nuo Nr.1 iki Nr. 17"))

    def test_OneHouse_TwoRanges_2(self):
        original = [ExpandedStreet(u"Respublikos gatvė", x) for x in [19, 26, 28]]
        original += [ExpandedStreet(u"Respublikos gatvė", 1, 17)]

        self.assertTuplesEqual(original, self.parser.ExpandStreet("Respublikos g. Nr. 19; Nr. 26; Nr. 28; numeriai nuo Nr.1 iki Nr. 17"))

    def test_(self):
        str = u"Chemikų g. neporiniai numeriai nuo Nr. 13 iki Nr. 31; poriniai nuo Nr. 130 iki Nr. 134."
        original = [ExpandedStreet(u"Chemikų gatvė", 13, 31),
                    ExpandedStreet(u"Chemikų gatvė", 130, 134)]

        self.assertTuplesEqual(original, self.parser.ExpandStreet(str))


    def test_OneHouse_TwoRanges(self):
        original = [ExpandedStreet(u"S. Dariaus ir S. Girėno gatvė", 1, ExpandedStreet.MaxOddValue),
                    ExpandedStreet(u"S. Dariaus ir S. Girėno gatvė", 4, ExpandedStreet.MaxEvenValue)]

        self.assertTuplesEqual(original, self.parser.ExpandStreet(u"S. Dariaus ir S. Girėno g. neporiniai numeriai nuo Nr. 1 iki galo; poriniai numeriai nuo Nr. 4 iki galo"))

    def test_OneHouse_WithSquare(self):
        original = [ExpandedStreet(u"Respublikos aikštė", 2)]
        self.assertTuplesEqual(original, self.parser.ExpandStreet(u"Respublikos a. Nr. 2"))

    def test_Number_WithLetter(self):
        original = [ExpandedStreet(u"Respublikos aikštė", "2D")]
        self.assertTuplesEqual(original, self.parser.ExpandStreet(u"Respublikos a. Nr. 2D"))


    def test_HouseNumberWithDot(self):
        original = [ExpandedStreet(u"Respublikos aikštė", 2)]
        self.assertTuplesEqual(original, self.parser.ExpandStreet(u"Respublikos a. Nr. 2."))


    def test_OneHouse_HouseNumber_WithLetter(self):

        original = [ExpandedStreet(u"S. Dariaus ir S. Girėno gatvė", 2)]
        self.assertTuplesEqual(original, self.parser.ExpandStreet(u"S. Dariaus ir S. Girėno g. numeriai nuo Nr. 2 iki Nr. 2A"))

    def test_OneHouse_WithDotInTheEnd(self):

        original = [ExpandedStreet(u"Naujosios gatvė", 4, 42)]

        self.assertTuplesEqual(original, self.parser.ExpandStreet("Naujosios g. poriniai numeriai nuo Nr. 4 iki Nr. 42."))

    def test_OneHouse_WithLetter_InStart(self):

        original = [ExpandedStreet(u"Vytauto gatvė", "3A"),
                    ExpandedStreet(u"Vytauto gatvė", 5, 11),
                    ExpandedStreet(u"Vytauto gatvė", 4, 10)]
        self.assertTuplesEqual(original, self.parser.ExpandStreet("Vytauto g. neporiniai numeriai nuo Nr. 3A iki Nr. 11; poriniai numeriai nuo Nr. 4 iki Nr. 10"))

    def test_NoSpaceBetweenStreet(self):
        original = [ExpandedStreet(u"Kuršių gatvė", 46, ExpandedStreet.MaxEvenValue)]

        self.assertTuplesEqual(original, self.parser.ExpandStreet(u"Kuršių g.poriniai numeriai nuo Nr. 46 iki galo"))

    def test_ifPreviousRangeIs_even_and_not_separated_by_semicolon_next_is_also_even(self):

        original = [ExpandedStreet(u"Visorių gatvė", 6, 8),
                    ExpandedStreet(u"Visorių gatvė", 14, 20)]

        self.assertTuplesEqual(original, self.parser.ExpandStreet(u"Visorių g. poriniai numeriai nuo Nr. 6 iki Nr. 8; nuo Nr. 14 iki Nr. 20."))

    def test_max_range_withou_even_or_odd_word(self):
        """ Range is given, but it does not say whether it is odd/even or both.
        If not given, look it up by what starting number is"""
        original = [ExpandedStreet(u"Olandų gatvė", 1, ExpandedStreet.MaxOddValue)]

        self.assertTuplesEqual(original, self.parser.ExpandStreet(u"Olandų g. numeriai nuo Nr. 1 iki galo"))

    def test_do_not_remove_house_letters(self):
        original = [ExpandedStreet(u"Pašilės gatvė", "39A"),
                ExpandedStreet(u"Pašilės gatvė", 41, 59)]

        self.assertTuplesEqual(original, self.parser.ExpandStreet(u"Pašilės g. neporiniai numeriai nuo Nr. 39A iki Nr. 59"))

    def test_do_not_remove_letter_no_range(self):
        original = [ExpandedStreet(u"Chemijos gatvė", "18B")]

        self.assertTuplesEqual(original, self.parser.ExpandStreet(u" Chemijos g. Nr. 18B"))





class TestAddressParser(TestCase):

    singleRecordFile = scriptPath + "/AkmenesDistrict_singleRecord.txt"

    def setUp(self):
        self.parser = AddressParser()


    def test_BugSBParsedIncorrectly(self):
        streetStr = "Vilnius: SB „Baldai“ Nr. 20, Nr. 27, Nr. 34A; SB „Ekspresas“, SB „Erškėtrožė“ Nr. 31, SB „Giedra“"
        parsed = list(self.parser.GetAddresses(streetStr))

        streets = ["SB „Baldai“ Nr. 20; Nr. 27; Nr. 34A",
                   "SB „Ekspresas“",
                   "SB „Erškėtrožė“ Nr. 31",
                   "SB „Giedra“"]

        for i in range(0, len(streets)):
            self.assertCity("Vilnius", streets[i], parsed[i])

        self.assertEqual(len(streets), len(parsed))

    def test_Bug007(self):
        streetStr = "Alytus: A. Jonyno g. neporiniai numeriai nuo Nr. 1 iki Nr. 17; Šaltinių g. neporiniai numeriai nuo Nr. 1 iki Nr. 17, Nr. 47, poriniai numeriai nuo Nr. 16 iki galo; numeriai nuo Nr. 2 iki Nr. 14; Žuvinto g. Nr. 13."

        parsed = list(self.parser.GetAddresses(streetStr))

        streets = ["A. Jonyno g. neporiniai numeriai nuo Nr. 1 iki Nr. 17",
                   "Šaltinių g. neporiniai numeriai nuo Nr. 1 iki Nr. 17; Nr. 47; poriniai numeriai nuo Nr. 16 iki galo; numeriai nuo Nr. 2 iki Nr. 14",
                   "Žuvinto g. Nr. 13."]

        for i in range(0, len(streets)):
            self.assertCity("Alytus", streets[i], parsed[i])

        self.assertEqual(len(streets), len(parsed))


    def test_Bug006(self):
        streetStr = "Vilnius: Apkasų g. neporiniai numeriai nuo Nr. 3 iki Nr. 5, poriniai numeriai nuo Nr. 2 iki Nr. 12A; J. Treinio g.; S. Žukausko g. Nr. 1, Nr. 2, poriniai numeriai nuo Nr. 16 iki Nr. 20A; Verkių g. Nr. 7, neporiniai numeriai nuo Nr. 13 iki Nr. 25B, poriniai numeriai nuo Nr. 14 iki Nr. 30A."

        parsed = list(self.parser.GetAddresses(streetStr))

        streets = ["Apkasų g. neporiniai numeriai nuo Nr. 3 iki Nr. 5; poriniai numeriai nuo Nr. 2 iki Nr. 12A",
                   "J. Treinio g.",
                   "S. Žukausko g. Nr. 1; Nr. 2; poriniai numeriai nuo Nr. 16 iki Nr. 20A",
                   "Verkių g. Nr. 7; neporiniai numeriai nuo Nr. 13 iki Nr. 25B; poriniai numeriai nuo Nr. 14 iki Nr. 30A."]
        for i in range(0, len(streets)):
            self.assertCity("Vilnius", streets[i], parsed[i])

        self.assertEqual(len(streets), len(parsed))

    def test_Bug005(self):
        """ some streets are not parsed"""
        streetStr = u"Panevėžys: Aldonos g.; Danutės g. neporiniai numeriai nuo Nr. 1 iki Nr. 27, poriniai numeriai nuo Nr. 2 iki Nr. 16; J. Tilvyčio g. neporiniai numeriai nuo Nr. 1 iki Nr. 35, poriniai numeriai nuo Nr. 2 iki Nr. 10; Katedros g., Katedros a.; Klaipėdos g. neporiniai numeriai nuo Nr. 3 iki Nr. 19; Krekenavos g. neporiniai numeriai nuo Nr. 1 iki galo; Nemuno g. poriniai numeriai nuo Nr. 2 iki Nr. 6; Nepriklausomybės a.; Ramygalos g. poriniai numeriai nuo Nr. 14 iki Nr. 50; S. Daukanto g. neporiniai numeriai nuo Nr. 39 iki Nr. 51; Sodų g., Vaižganto g., Varnaičių g.; Vysk. K. Paltaroko g. neporiniai numeriai nuo Nr. 1 iki galo; poriniai numeriai nuo Nr. 2 iki Nr. 16."

        parsed = list(self.parser.GetAddresses(streetStr))

        streets = [u"Aldonos g.",
                   u"Danutės g. neporiniai numeriai nuo Nr. 1 iki Nr. 27; poriniai numeriai nuo Nr. 2 iki Nr. 16",
                   u"J. Tilvyčio g. neporiniai numeriai nuo Nr. 1 iki Nr. 35; poriniai numeriai nuo Nr. 2 iki Nr. 10",
                   u"Katedros g.",
                   u"Katedros a.",
                   u"Klaipėdos g. neporiniai numeriai nuo Nr. 3 iki Nr. 19",
                   u"Krekenavos g. neporiniai numeriai nuo Nr. 1 iki galo",
                   u"Nemuno g. poriniai numeriai nuo Nr. 2 iki Nr. 6",
                   u"Nepriklausomybės a.",
                   u"Ramygalos g. poriniai numeriai nuo Nr. 14 iki Nr. 50",
                   u"S. Daukanto g. neporiniai numeriai nuo Nr. 39 iki Nr. 51",
                   u"Sodų g.",
                   u"Vaižganto g.",
                   u"Varnaičių g.",
                   u"Vysk. K. Paltaroko g. neporiniai numeriai nuo Nr. 1 iki galo; poriniai numeriai nuo Nr. 2 iki Nr. 16."]

        for i in range(0, len(streets)):
            self.assertCity(u"Panevėžys", streets[i], parsed[i])

        self.assertEqual(len(streets), len(parsed))

    def test_Bug004(self):
        """ some streets are not recognized correctly"""
        streetStr = "Kaunas: A. Jakšto g., Aleksoto g., Bernardinų skg., Birštono g., D. Poškos g., Druskininkų g.; I. Kanto g. neporiniai numeriai nuo Nr. 1 iki galo; J. Gruodžio g., J. Naugardo g., Jėzuitų skg.; Karaliaus Mindaugo pr. neporiniai numeriai nuo Nr. 1 iki Nr. 25, poriniai numeriai nuo Nr. 2 iki Nr. 26; Kurpių g., L. Zamenhofo g.; Laisvės al. neporiniai numeriai nuo Nr. 95 iki galo; M. Daukšos g. neporiniai numeriai nuo Nr. 1 iki Nr. 17, poriniai numeriai nuo Nr. 2 iki Nr. 12; M. Valančiaus g. neporiniai numeriai nuo Nr. 1 iki galo; Muitinės g., Muziejaus g., Nemuno g., Palangos g., Papilio g., Pilies g., Prieplaukos Krantinės g., Puodžių g.; Raguvos g. neporiniai numeriai nuo Nr. 7 iki Nr. 11, poriniai numeriai nuo Nr. 2 iki Nr. 10A; Rotušės a., Santakos g., Šilutės g., Smalininkų g., T. Daugirdo g., Trimito g., V. Kuzmos g.; Vilniaus g. poriniai numeriai nuo Nr. 2 iki galo."

        parsed = list(self.parser.GetAddresses(streetStr))

        streets = ["A. Jakšto g.",
                   "Aleksoto g.",
                   "Bernardinų skg.",
                   "Birštono g.",
                   "D. Poškos g.",
                   "Druskininkų g.",
                   "I. Kanto g. neporiniai numeriai nuo Nr. 1 iki galo",
                   "J. Gruodžio g.",
                   "J. Naugardo g.",
                   "Jėzuitų skg.",
                   "Karaliaus Mindaugo pr. neporiniai numeriai nuo Nr. 1 iki Nr. 25; poriniai numeriai nuo Nr. 2 iki Nr. 26",
                   "Kurpių g.",
                   "L. Zamenhofo g.",
                   "Laisvės al. neporiniai numeriai nuo Nr. 95 iki galo",
                   "M. Daukšos g. neporiniai numeriai nuo Nr. 1 iki Nr. 17; poriniai numeriai nuo Nr. 2 iki Nr. 12",
                   "M. Valančiaus g. neporiniai numeriai nuo Nr. 1 iki galo",
                   "Muitinės g.",
                   "Muziejaus g.",
                   "Nemuno g.",
                   "Palangos g.",
                   "Papilio g.",
                   "Pilies g.",
                   "Prieplaukos Krantinės g.",
                   "Puodžių g.",
                   "Raguvos g. neporiniai numeriai nuo Nr. 7 iki Nr. 11; poriniai numeriai nuo Nr. 2 iki Nr. 10A",
                   "Rotušės a.",
                   "Santakos g.",
                   "Šilutės g.",
                   "Smalininkų g.",
                   "T. Daugirdo g.",
                   "Trimito g.",
                   "V. Kuzmos g.",
                   "Vilniaus g. poriniai numeriai nuo Nr. 2 iki galo."]

        for i in range(0, len(streets)):
            self.assertCity("Kaunas", streets[i], parsed[i])

        self.assertEqual(len(streets), len(parsed))


    def test_Bug003(self):
        """ endings with "nuo nr 70 iki galo" are treated as sepearete streats """
        streetStr = "Kaunas: 9-ojo Forto g. poriniai numeriai nuo Nr. 2 iki Nr. 18; A. Šapokos g., A. Žmuidzinavičiaus g., Adomynės g., Adutiškio g., Alytaus g., B. Brazdžionio g., Bačkonių g., Baisiogalos g.; Baltijos g. poriniai numeriai nuo Nr. 106 iki galo; Bernatonių g., Bražuolės g., E. Cinzo g., Eidintų g., Eigirgalos g., Gabijos g., Girios g., J. Bielinio g.; J. Semaškos g. neporiniai numeriai nuo Nr. 37 iki galo; poriniai numeriai nuo Nr. 36 iki galo; J. Skvirecko g.; Josvainių g. Nr. 1; Klovainių g., Knygnešių g., Kražių g., Kriaučiūnų g., Labūnavos g., Lapkalnio g., Liucernų g.; Liucijanavos g. poriniai numeriai nuo Nr. 2 iki galo; Miežėnų g.; Mosėdžio g. neporiniai numeriai nuo Nr. 65 iki galo; Naujakurių g. neporiniai numeriai nuo Nr. 37 iki galo; poriniai numeriai nuo Nr. 58 iki Nr. 58A, nuo Nr. 70 iki galo; P. Rusecko g., Pakalnučių g., Pakaunės g., Pokšniabalio g., Prūsų g. neporiniai numeriai nuo Nr. 1 iki galo; Rainių g., S. Banaičio g., Šalčininkų g., Šaltupio g., Sėlių g., Šėtos g., Šilagirio g.; Šilainių pl. neporiniai numeriai nuo Nr. 1 iki Nr. 21P, poriniai numeriai nuo Nr. 2 iki galo; Šilo g., Šiluvos g., Ugnės g., Vakarinio Aplinkkelio g., Žalčio Karūnos al., Žemynos g."

        parsed = list(self.parser.GetAddresses(streetStr))

        streets= ["9-ojo Forto g. poriniai numeriai nuo Nr. 2 iki Nr. 18",
                  "A. Šapokos g.",
                  "A. Žmuidzinavičiaus g.",
                  "Adomynės g.",
                  "Adutiškio g.",
                  "Alytaus g.",
                  "B. Brazdžionio g.",
                  "Bačkonių g.",
                  "Baisiogalos g.",
                  "Baltijos g. poriniai numeriai nuo Nr. 106 iki galo",
                  "Bernatonių g.",
                  "Bražuolės g.",
                  "E. Cinzo g.",
                  "Eidintų g.",
                  "Eigirgalos g.",
                  "Gabijos g.",
                  "Girios g.",
                  "J. Bielinio g.",
                  "J. Semaškos g. neporiniai numeriai nuo Nr. 37 iki galo; poriniai numeriai nuo Nr. 36 iki galo",
                  "J. Skvirecko g.",
                  "Josvainių g. Nr. 1",
                  "Klovainių g.",
                  "Knygnešių g.",
                  "Kražių g.",
                  "Kriaučiūnų g.",
                  "Labūnavos g.",
                  "Lapkalnio g.",
                  "Liucernų g.",
                  "Liucijanavos g. poriniai numeriai nuo Nr. 2 iki galo",
                  "Miežėnų g.",
                  "Mosėdžio g. neporiniai numeriai nuo Nr. 65 iki galo",
                  "Naujakurių g. neporiniai numeriai nuo Nr. 37 iki galo; poriniai numeriai nuo Nr. 58 iki Nr. 58A; nuo Nr. 70 iki galo",
                  "P. Rusecko g.",
                  "Pakalnučių g.",
                  "Pakaunės g.",
                  "Pokšniabalio g.",
                  "Prūsų g. neporiniai numeriai nuo Nr. 1 iki galo",
                  "Rainių g.",
                  "S. Banaičio g.",
                  "Šalčininkų g.",
                  "Šaltupio g.",
                  "Sėlių g.",
                  "Šėtos g.",
                  "Šilagirio g.",
                  "Šilainių pl. neporiniai numeriai nuo Nr. 1 iki Nr. 21P; poriniai numeriai nuo Nr. 2 iki galo",
                  "Šilo g.",
                  "Šiluvos g.",
                  "Ugnės g.",
                  "Vakarinio Aplinkkelio g.",
                  "Žalčio Karūnos al.",
                  "Žemynos g."]

        for i in range(0, len(streets)):
            self.assertCity("Kaunas", streets[i], parsed[i])

        self.assertEqual(len(streets), len(parsed))

    def test_Bug002(self):
        streetStr = "Kaunas: Naujakurių g. neporiniai numeriai nuo Nr. 37 iki galo; poriniai numeriai nuo Nr. 58 iki Nr. 58A, nuo Nr. 70 iki galo;"
        parsed = list(self.parser.GetAddresses(streetStr))
        self.assertCity("Kaunas", "Naujakurių g. neporiniai numeriai nuo Nr. 37 iki galo; poriniai numeriai nuo Nr. 58 iki Nr. 58A; nuo Nr. 70 iki galo", parsed[0])
        self.assertEqual(1, len(parsed))

    def test_Bug001(self):
        streetStr = "Kaunas: A. Stulginskio g. neporiniai numeriai nuo Nr. 61 iki galo; poriniai numeriai nuo Nr. 54 iki galo; Bajorų g., Panerių g. poriniai numeriai nuo Nr. 72 iki Nr. 90; Sąjungos a. neporiniai numeriai nuo Nr. 1 iki Nr. 3, nuo Nr. 5 iki galo; Varnių g. poriniai numeriai nuo Nr. 22 iki Nr. 38."
        parsed = list(self.parser.GetAddresses(streetStr))
        self.assertCity("Kaunas", "A. Stulginskio g. neporiniai numeriai nuo Nr. 61 iki galo; poriniai numeriai nuo Nr. 54 iki galo", parsed[0])
        self.assertCity("Kaunas", "Bajorų g.", parsed[1])
        self.assertCity("Kaunas", "Panerių g. poriniai numeriai nuo Nr. 72 iki Nr. 90", parsed[2])
        self.assertCity("Kaunas", "Sąjungos a. neporiniai numeriai nuo Nr. 1 iki Nr. 3; nuo Nr. 5 iki galo", parsed[3])
        self.assertCity("Kaunas", "Varnių g. poriniai numeriai nuo Nr. 22 iki Nr. 38.", parsed[4])
        self.assertEqual(5, len(parsed))

    def test_plentas(self):
        streetStr = "Kaunas: Arnavos g.; Baltų pr. neporiniai numeriai nuo Nr. 11A iki Nr. 85A, poriniai numeriai nuo Nr. 28 iki Nr. 38; Lazdynėlių g.; Mosėdžio g. neporiniai numeriai nuo Nr. 1 iki Nr. 29, poriniai numeriai nuo Nr. 2 iki Nr. 18, nuo Nr. 24 iki Nr. 28; Nadruvių g., Notangų g., Pagudėnų g., Pamedėnų g., Pilupėnų g., Šateikių g., Sembų g., Skalvių g., Stalupėnų g., Tolminkiemio g., Žemaičių pl. neporiniai numeriai nuo Nr. 23 iki Nr. 25."
        parsed = list(self.parser.GetAddresses(streetStr))
        self.assertCity("Kaunas", "Arnavos g.", parsed[0])
        self.assertCity("Kaunas", "Baltų pr. neporiniai numeriai nuo Nr. 11A iki Nr. 85A; poriniai numeriai nuo Nr. 28 iki Nr. 38", parsed[1])
        self.assertCity("Kaunas", "Lazdynėlių g.", parsed[2])
        self.assertCity("Kaunas", "Mosėdžio g. neporiniai numeriai nuo Nr. 1 iki Nr. 29; poriniai numeriai nuo Nr. 2 iki Nr. 18; nuo Nr. 24 iki Nr. 28", parsed[3])
        self.assertCity("Kaunas", "Nadruvių g.", parsed[4])
        self.assertCity("Kaunas", "Notangų g.", parsed[5])
        self.assertCity("Kaunas", "Pagudėnų g.", parsed[6])
        self.assertCity("Kaunas", "Pamedėnų g.", parsed[7])
        self.assertCity("Kaunas", "Pilupėnų g.", parsed[8])
        self.assertCity("Kaunas", "Šateikių g.", parsed[9])
        self.assertCity("Kaunas", "Sembų g.", parsed[10])
        self.assertCity("Kaunas", "Skalvių g.", parsed[11])
        self.assertCity("Kaunas", "Stalupėnų g.", parsed[12])
        self.assertCity("Kaunas", "Tolminkiemio g.", parsed[13])
        self.assertCity("Kaunas", "Žemaičių pl. neporiniai numeriai nuo Nr. 23 iki Nr. 25.", parsed[14])
        self.assertEqual(15, len(parsed))

    def test_Poriniai_Neporiniai(self):
        streetStr = "Alytus: A. Baranausko g., A. Matučio g., A. Žmuidzinavičiaus g., Alyvų Tako g. neporiniai numeriai nuo Nr. 17 iki galo; poriniai numeriai nuo Nr. 10 iki galo; numeriai nuo Nr. 1 iki Nr. 8; Alyvų Tako 2 g., Dzūkų g., J. Basanavičiaus g., J. Tumo-Vaižganto g., Kranto g., Kurorto g., Lelijų g., M. K. Čiurlionio g., Maironio g., Nemuno g., Pliažo g., Pušyno g.; S. Dariaus ir S. Girėno g. neporiniai numeriai nuo Nr. 1 iki galo; poriniai numeriai nuo Nr. 4 iki galo; Savanorių g., Šilelio g., Šilo g., Sporto g., Tako I g., Tako II g., Tilto g., Užuovėjos g., V. Krėvės g., V. Kudirkos g., Žemaitės g."
        parsed = list(self.parser.GetAddresses(streetStr))

        self.assertCity("Alytus", "A. Baranausko g.", parsed[0])
        self.assertCity("Alytus", "A. Matučio g.", parsed[1])
        self.assertCity("Alytus", "A. Žmuidzinavičiaus g.", parsed[2])
        self.assertCity("Alytus", "Alyvų Tako g. neporiniai numeriai nuo Nr. 17 iki galo; poriniai numeriai nuo Nr. 10 iki galo; numeriai nuo Nr. 1 iki Nr. 8", parsed[3])
        self.assertCity("Alytus", "Alyvų Tako 2 g.", parsed[4])
        self.assertCity("Alytus", "Dzūkų g.", parsed[5])
        self.assertCity("Alytus", "J. Basanavičiaus g.", parsed[6])
        self.assertCity("Alytus", "J. Tumo-Vaižganto g.", parsed[7])
        self.assertCity("Alytus", "Kranto g.", parsed[8])
        self.assertCity("Alytus", "Kurorto g.", parsed[9])
        self.assertCity("Alytus", "Lelijų g.", parsed[10])
        self.assertCity("Alytus", "M. K. Čiurlionio g.", parsed[11])
        self.assertCity("Alytus", "Maironio g.", parsed[12])
        self.assertCity("Alytus", "Nemuno g.", parsed[13])
        self.assertCity("Alytus", "Pliažo g.", parsed[14])
        self.assertCity("Alytus", "Pušyno g.", parsed[15])
        self.assertCity("Alytus", "S. Dariaus ir S. Girėno g. neporiniai numeriai nuo Nr. 1 iki galo; poriniai numeriai nuo Nr. 4 iki galo", parsed[16])
        self.assertCity("Alytus", "Savanorių g.", parsed[17])
        self.assertCity("Alytus", "Šilelio g.", parsed[18])
        self.assertCity("Alytus", "Šilo g.", parsed[19])
        self.assertCity("Alytus", "Sporto g.", parsed[20])
        self.assertCity("Alytus", "Tako I g.", parsed[21])
        self.assertCity("Alytus", "Tako II g.", parsed[22])
        self.assertCity("Alytus", "Tilto g.", parsed[23])
        self.assertCity("Alytus", "Užuovėjos g.", parsed[24])
        self.assertCity("Alytus", "V. Krėvės g.", parsed[25])
        self.assertCity("Alytus", "V. Kudirkos g.", parsed[26])
        self.assertCity("Alytus", "Žemaitės g.", parsed[27])
        self.assertEqual(28, len(parsed))

    def test_SmallCity(self):
        streetStr = u"Apušroto k., Biržų k., Bražiškių k., Dovydžių k., Dulbių k., Gembūčių k., Gerkiškių k., Kalnelio k., Karniškių k., Kruopių mstl., Laumėnų I k., Laumėnų II k., Liepkalnio k., Maušų k., Narbūčių k., Pagervių k. dalis, Pagervių k., Rudeliškių k., Saunorių I k., Saunorių II k., Senlaukio k., Spaigių k., Šiauliukų k., Šliupščių k., Vilkaičių k."
        parsed = list(self.parser.GetAddresses(streetStr))
        self.assertCity(u"Apušroto kaimas",      "", parsed[0])
        self.assertCity(u"Biržų kaimas",         "", parsed[1])
        self.assertCity(u"Bražiškių kaimas",     "", parsed[2])
        self.assertCity(u"Dovydžių kaimas",      "", parsed[3])
        self.assertCity(u"Dulbių kaimas",        "", parsed[4])
        self.assertCity(u"Gembūčių kaimas",      "", parsed[5])
        self.assertCity(u"Gerkiškių kaimas",     "", parsed[6])
        self.assertCity(u"Kalnelio kaimas",      "", parsed[7])
        self.assertCity(u"Karniškių kaimas",     "", parsed[8])
        self.assertCity(u"Kruopių miestelis",    "", parsed[9])
        self.assertCity(u"Laumėnų I kaimas",     "", parsed[10])
        self.assertCity(u"Laumėnų II kaimas",    "", parsed[11])
        self.assertCity(u"Liepkalnio kaimas",    "", parsed[12])
        self.assertCity(u"Maušų kaimas",         "", parsed[13])
        self.assertCity(u"Narbūčių kaimas",      "", parsed[14])
        self.assertCity(u"Pagervių kaimas",      "", parsed[15])
        self.assertCity(u"Pagervių kaimas",      "", parsed[16])
        self.assertCity(u"Rudeliškių kaimas",    "", parsed[17])
        self.assertCity(u"Saunorių I kaimas",    "", parsed[18])
        self.assertCity(u"Saunorių II kaimas",   "", parsed[19])
        self.assertCity(u"Senlaukio kaimas",     "", parsed[20])
        self.assertCity(u"Spaigių kaimas",       "", parsed[21])
        self.assertCity(u"Šiauliukų kaimas",     "", parsed[22])
        self.assertCity(u"Šliupščių kaimas",     "", parsed[23])
        self.assertCity(u"Vilkaičių kaimas",     "", parsed[24])
        self.assertEqual(25, len(parsed))


    def assertCity(self, cityName, streetName, cityAddress):
        self.assertEqual(cityName, cityAddress.cityName)
        self.assertEqual(streetName, cityAddress.streetName)

    def test_Street_WithPoriniai(self):
        streetStr = u"Naujoji Akmenė: Respublikos g. Nr. 19, Nr. 26, Nr. 28, numeriai nuo Nr. 1 iki Nr. 17; Respublikos a. Nr. 2."
        parsed = list(self.parser.GetAddresses(streetStr))
        self.assertCity(u"Naujoji Akmenė", u"Respublikos g. Nr. 19; Nr. 26; Nr. 28; numeriai nuo Nr. 1 iki Nr. 17", parsed[0])
        self.assertCity(u"Naujoji Akmenė", u"Respublikos a. Nr. 2.", parsed[1])
        self.assertEqual(2, len(parsed))

    def test_Street_WithHouseNumbers(self):
        streetStr = u"Naujoji Akmenė: Respublikos g. Nr. 18, Nr. 20, Nr. 21, Nr. 23, Nr. 24, Nr. 25, Nr. 27; SB „Ąžuolas“, V. Kudirkos g."
        parsed = list(self.parser.GetAddresses(streetStr))
        self.assertCity(u"Naujoji Akmenė", u"Respublikos g. Nr. 18; Nr. 20; Nr. 21; Nr. 23; Nr. 24; Nr. 25; Nr. 27", parsed[0])
        self.assertCity(u"Naujoji Akmenė", u"SB „Ąžuolas“", parsed[1])
        self.assertCity(u"Naujoji Akmenė", u"V. Kudirkos g.", parsed[2])
        self.assertEqual(3, len(parsed))



    def test_TwoCities(self):
        streetStr = u"Gajauciškio k., Gemaitiškių k., Jurkionių k.: SB „Dzūkija“, Medukštos k., Navasiolkų k., Norgeliškių k., Padvariškių k., Panemuninkėlių k.; Panemuninkų k.: SB „Versmė“; Raganiškių k., Strielčių k., Taučionių k., Vaidaugų k., Vaisodžių k., Vaišupio k., Valiūnų k., Žiūkų k."
        parsed = list(self.parser.GetAddresses(streetStr))
        self.assertCity(u"Gajauciškio kaimas", "", parsed[0])
        self.assertCity(u"Gemaitiškių kaimas", "", parsed[1])
        self.assertCity(u"Jurkionių kaimas", u"SB „Dzūkija“", parsed[2])
        self.assertCity(u"Medukštos kaimas", "", parsed[3])
        self.assertCity(u"Navasiolkų kaimas", "", parsed[4])
        self.assertCity(u"Norgeliškių kaimas", "", parsed[5])
        self.assertCity(u"Padvariškių kaimas", "", parsed[6] )
        self.assertCity(u"Panemuninkėlių kaimas", "", parsed[7])
        self.assertCity(u"Panemuninkų kaimas", u"SB „Versmė“", parsed[8])
        self.assertCity(u"Raganiškių kaimas", "", parsed[9])
        self.assertCity(u"Strielčių kaimas", "", parsed[10])
        self.assertCity(u"Taučionių kaimas", "", parsed[11])
        self.assertCity(u"Vaidaugų kaimas", "", parsed[12]  )
        self.assertCity(u"Vaisodžių kaimas", "", parsed[13]  )
        self.assertCity(u"Vaišupio kaimas", "", parsed[14])
        self.assertCity(u"Valiūnų kaimas", "", parsed[15])
        self.assertCity(u"Žiūkų kaimas", "", parsed[16])
        self.assertEqual(17, len(parsed))

    def test_Villages_And_OneCity(self):
        streetStr = u"Bažavos k., Kolonistų k.; Simnas: Alytaus g., Ateities g., Birutės g., Dariaus ir Girėno g., Draugystės g., Ežero g., Jaunimo g., Kaimynų g., Kreivoji g., Laisvės g., Melioratorių g., Naujoji g., Paupio g., Pavasario g., S. Nėries g., Saulėtekio g., Šviesos g., Taikos g., Vanagėlio g., Vytauto g., Žalioji g., Žemaitės g."

        parsed = list(self.parser.GetAddresses(streetStr))
        bazavos = parsed[0]
        kolonistu = parsed[1]
        simnasAlytaus = parsed[2]
        simnasAteities = parsed[3]
        simnasBirutes = parsed[4]
        self.assertCity(u"Bažavos kaimas", u"", bazavos)
        self.assertCity(u"Kolonistų kaimas", u"", kolonistu)
        self.assertCity(u"Simnas", u"Alytaus g.", simnasAlytaus)
        self.assertCity(u"Simnas", u"Ateities g.", simnasAteities)
        self.assertCity(u"Simnas", u"Birutės g.", simnasBirutes)

        self.assertEqual(24, len(parsed))


    def test_OneCity_ManyStreets(self):
        file = open(self.singleRecordFile, "r")
        importer = LithuanianConstituencyReader(file)
        loc = list(importer.getLocations())[0]

        addressStr = loc.Addresses

        parsed = list(self.parser.GetAddresses(addressStr))

        self.assertCity(u"Naujoji Akmenė", u"Algirdo g.", parsed[0])

        self.assertCity(u"Naujoji Akmenė", u"Aušros g.", parsed[1])

        self.assertEqual(55, len(parsed))

        """Naujoji Akmenė: Algirdo g., Aušros g., Barvydžio vs., Beržyno g.,
Botanikos sodas „Puošmena“, Čiapo vs., Dambrausko vs., Darbininkų g.,
Eibučių g., Gedimino g., Gintausko vs., Guginio vs., J. Dalinkevičiaus"""
