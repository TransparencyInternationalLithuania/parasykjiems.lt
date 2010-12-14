#!/usr/bin/env python
# -*- coding: utf-8 -*-

from cdb_lt_mps.parseConstituencies import PollingDistrictStreetExpander, ExpandedStreet, LithuanianConstituencyParser, LithuanianConstituencyReader, AddressParser
from django.test.testcases import TestCase
from cdb_lt_mps.management.commands.importMPs import LithuanianMPsReader
import os


scriptPath = os.path.dirname( os.path.realpath( __file__ ) )

class TestImportLithuanianCounties(TestCase):
    singleRecordFile = scriptPath + "/AkmenesDistrict_singleRecord.txt"
    alytusRecordFile = scriptPath + "/AlytausMiestas.txt"
    allRecords = scriptPath + "/Apygardos.txt"



    def countNumberOfRecords(self, fileName):
        file = open(fileName, "r")
        importer = LithuanianConstituencyReader(file)
        count = 0
        for l in importer.getLocations():
            count += 1
        return count

    def test_AllRecors_count(self):
        self.assertEqual(self.countNumberOfRecords(self.allRecords), 2034)

    def test_Alytaus_count(self):
        self.assertEqual(self.countNumberOfRecords(self.alytusRecordFile), 24)

    def test_Akmenes_count(self):
        self.assertEqual(self.countNumberOfRecords(self.singleRecordFile), 1)

    def assertPollingDistrict(self, allPollingDistricts, pollingDistrict, constituency, district,
                              pollingDistrictAddress = None, numberOfVoters = None):

        parser = LithuanianConstituencyParser()
        constituency = parser.ExtractConstituencyFromConstituencyFile(constituency)

        pd = allPollingDistricts[self.getKey(pollingDistrict, constituency)]
        if (pd == None):
            self.fail("Could not find polling district %s" % pollingDistrict)

        self.assertEqual(constituency.nr, pd.Constituency.nr)
        self.assertEqual(constituency.name, pd.Constituency.name)
        self.assertEqual(pollingDistrict, pd.PollingDistrict)
        self.assertEqual(district, pd.District)

        if (pollingDistrictAddress is not None):
            self.assertEqual(pollingDistrictAddress, pd.pollingDistrictAddress)

        if (numberOfVoters is not None):
            self.assertEqual(numberOfVoters, pd.numberOfVoters)


    def getKey(self, pollingDistrict, constituency):
        return "%s - %s %d" % (pollingDistrict, constituency.name, constituency.nr)

    def test_DistrictNames(self):
        # find a polling district and assert that district is correct
        allPollingDistricts = {}
        file = open(self.allRecords, "r")

        # probably this line can be even further reduced in length, help would be welcome
        for pollingDistrict in LithuanianConstituencyReader(file).getLocations():
            allPollingDistricts[self.getKey(pollingDistrict.PollingDistrict, pollingDistrict.Constituency)] = pollingDistrict

        self.assertPollingDistrict  (allPollingDistricts, u"Senamiesčio rinkimų apylinkė Nr. 1", u"Akmenės–Joniškio rinkimų apygarda Nr. 39", u"Akmenės rajonAS", u"Adresas *Vytauto g. 3, Naujoji Akmenė.", u"Rinkėjų skaičius *2632.")
        self.assertPollingDistrict(allPollingDistricts, u"Lomenos rinkimų apylinkė Nr. 4", u"Kaišiadorių–Elektrėnų rinkimų apygarda Nr. 59", u"Kaišiadorių rajonAS")
        self.assertPollingDistrict(allPollingDistricts, u"Girelės rinkimų apylinkė Nr. 3", u"Kaišiadorių–Elektrėnų rinkimų apygarda Nr. 59", u"Kaišiadorių rajonAS", u"Adresas *Girelės g. 53, Kaišiadorys, Technologijų ir verslo mokyklos bendrabučio salė.", u"Rinkėjų skaičius *2789.")

        self.assertPollingDistrict(allPollingDistricts, u"S. Daukanto rinkimų apylinkė Nr. 64", u"Danės rinkimų apygarda Nr. 19", u"Klaipėdos miestas", u"Adresas *S.Daukanto g. 5, Klaipėda.", u"Rinkėjų skaičius *1001.")



    def test_Akmenes_read_record(self):

        file = open(self.singleRecordFile, "r")
        importer = LithuanianConstituencyReader(file)
        for loc in importer.getLocations():
            self.assertEqual(loc.District, u"Akmenės rajonAS")
            self.assertEqual(loc.Constituency.name, u"Akmenės–Joniškio rinkimų apygarda")
            self.assertEqual(loc.Constituency.nr, 39)
            self.assertEqual(loc.PollingDistrict, u"Senamiesčio rinkimų apylinkė Nr. 1")
            self.assertTrue(loc.Addresses.index(u"Naujoji Akmenė: Algirdo g., Aušros g., Barvydžio vs.,") >= 0)

class TestLithuanianConstituencyParser(TestCase):
    parser = LithuanianConstituencyParser()

    def test_ExtractConstituencyFromConstituencyFile(self):
        Constituency = self.parser.ExtractConstituencyFromConstituencyFile("Lazdynų rinkimų apygarda Nr. 9")
        self.assertEqual("Lazdynų rinkimų apygarda", Constituency.name)
        self.assertEqual(9, Constituency.nr)

    def test_ExtractConstituencyFromMPsFile(self):
        Constituency = self.parser.ExtractConstituencyFromMPsFile("Naujamiesčio (Nr. 1)")
        self.assertEqual("Naujamiesčio", Constituency.name)
        self.assertEqual(1, Constituency.nr)

class TestReadParliamentMembers(TestCase):
    allRecords = scriptPath + "/parliament members.txt"

    def countNumberOfRecords(self, fileName):
        reader = LithuanianMPsReader(fileName)
        count = 0
        for l in reader.ReadParliamentMembers():
            count += 1
        return count

    def test_AllRecors_count(self):
        self.assertEqual(self.countNumberOfRecords(self.allRecords), 71)

    def test_Read_first_record(self):

        reader = LithuanianMPsReader(self.allRecords)
        for loc in reader.ReadParliamentMembers():
            self.assertEqual(loc.constituency.nr, 1)
            self.assertEqual(loc.constituency.name, "Naujamiesčio")
            self.assertEqual(loc.name, "Irena")
            self.assertEqual(loc.surname, u"Degutienė")
            self.assertEqual(loc.email, "Irena.Degutiene@lrs.lt, irdegu@lrs.lt")
            break;

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
        original = [ExpandedStreet(street = "Mano g.")]
        self.assertTuplesEqual(original, self.parser.ExpandStreet("Mano g."))

    def test_street_pr(self):
        original = [ExpandedStreet("Baltų pr.", 1), ExpandedStreet("Baltų pr.", 2)]
        self.assertTuplesEqual(original, self.parser.ExpandStreet("Baltų pr. Nr.1; Nr. 2"))

    def test_street_pl(self):
        original = [ExpandedStreet("Baltų pl.", 1), ExpandedStreet("Baltų pl.", 2)]
        self.assertTuplesEqual(original, self.parser.ExpandStreet("Baltų pl. Nr.1; Nr. 2"))

    def test_street_al(self):
        original = [ExpandedStreet("Baltų al.", 1), ExpandedStreet("Baltų al.", 2)]
        self.assertTuplesEqual(original, self.parser.ExpandStreet("Baltų al. Nr.1; Nr. 2"))

    def test_SB(self):
        original = [ExpandedStreet("SB Dailė.", 1), ExpandedStreet("SB Dailė.", 2)]
        self.assertTuplesEqual(original, self.parser.ExpandStreet("SB Dailė. Nr.1; Nr. 2"))
        #SB „Dailė“ Nr. 1, Nr. 27, Nr. 30, Nr. 50, Nr. 52, Nr. 56



    def test_OneHouse(self):

        vec = [18, 20, 22, 24, 26, 27, 29]
        original = [ExpandedStreet("Respublikos g.", x) for x in vec]

        self.assertTuplesEqual(original, self.parser.ExpandStreet("Respublikos g. Nr. 18; Nr. 20; Nr. 22; Nr. 24; Nr. 26; Nr. 27; Nr. 29"))

    def test_OneHouse_OneContinuosRange(self):
        original = [ExpandedStreet("Respublikos g.", 1, 17)]
        self.assertTuplesEqual(original, self.parser.ExpandStreet("Respublikos g. poriniai numeriai nuo Nr.1 iki Nr. 17"))

    def test_OneHouse_TwoRanges_2(self):
        vec = [19, 26, 28]
        original = [ExpandedStreet("Respublikos g.", x) for x in vec]
        original += [ExpandedStreet("Respublikos g.", 1, 17),
                     ExpandedStreet("Respublikos g.", 2, 16)]

        self.assertTuplesEqual(original, self.parser.ExpandStreet("Respublikos g. Nr. 19; Nr. 26; Nr. 28; numeriai nuo Nr.1 iki Nr. 17"))

    def test_(self):
        str = "Chemikų g. neporiniai numeriai nuo Nr. 13 iki Nr. 31; nuo Nr. 130 iki Nr. 134."
        original = [ExpandedStreet("Chemikų g.", 13, 31),
                    ExpandedStreet("Chemikų g.", 131, 133),
                    ExpandedStreet("Chemikų g.", 130, 134)]

        self.assertTuplesEqual(original, self.parser.ExpandStreet(str))


    def test_OneHouse_TwoRanges(self):
        original = [ExpandedStreet("S. Dariaus ir S. Girėno g.", 1, ExpandedStreet.MaxOddValue),
                    ExpandedStreet("S. Dariaus ir S. Girėno g.", 4, ExpandedStreet.MaxEvenValue)]

        self.assertTuplesEqual(original, self.parser.ExpandStreet("S. Dariaus ir S. Girėno g. neporiniai numeriai nuo Nr. 1 iki galo; poriniai numeriai nuo Nr. 4 iki galo"))

    def test_OneHouse_ThreeRanges(self):
        original = [ExpandedStreet("AlyvųTako g.", 17, ExpandedStreet.MaxOddValue),
                    ExpandedStreet("AlyvųTako g.", 10, ExpandedStreet.MaxEvenValue),
                    ExpandedStreet("AlyvųTako g.", 1, 7),
                    ExpandedStreet("AlyvųTako g.", 2, 8)]

        self.assertTuplesEqual(original, self.parser.ExpandStreet("AlyvųTako g. neporiniai numeriai nuo Nr. 17 iki galo; poriniai numeriai nuo Nr. 10 iki galo; numeriai nuo Nr. 1 iki Nr. 8"))

    def test_OneHouse_WithSquare(self):
        original = [ExpandedStreet("Respublikos a.", 2)]
        self.assertTuplesEqual(original, self.parser.ExpandStreet("Respublikos a. Nr. 2"))

    def test_Number_WithLetter(self):
        original = [ExpandedStreet("Respublikos a.", 2)]
        self.assertTuplesEqual(original, self.parser.ExpandStreet("Respublikos a. Nr. 2D"))


    def test_HouseNumberWithDot(self):
        original = [ExpandedStreet("Respublikos a.", 2)]
        self.assertTuplesEqual(original, self.parser.ExpandStreet("Respublikos a. Nr. 2."))


    def test_OneHouse_HouseNumber_WithLetter(self):

        original = [ExpandedStreet("S. Dariaus ir S. Girėno g.", 2)]
        self.assertTuplesEqual(original, self.parser.ExpandStreet("S. Dariaus ir S. Girėno g. numeriai nuo Nr. 2 iki Nr. 2A"))

    def test_OneHouse_WithDotInTheEnd(self):

        original = [ExpandedStreet("Naujosios g.", 4, 42)]

        self.assertTuplesEqual(original, self.parser.ExpandStreet("Naujosios g. poriniai numeriai nuo Nr. 4 iki Nr. 42."))

    def test_OneHouse_WithLetter_InStart(self):

        original = [ExpandedStreet("Vytauto g.", 3, 11),
                    ExpandedStreet("Vytauto g.", 4, 10)]
        self.assertTuplesEqual(original, self.parser.ExpandStreet("Vytauto g. neporiniai numeriai nuo Nr. 3A iki Nr. 11; poriniai numeriai nuo Nr. 4 iki Nr. 10"))

    def test_NoSpaceBetweenStreet(self):
        original = [ExpandedStreet("Kuršių g.", 46, ExpandedStreet.MaxEvenValue)]

        self.assertTuplesEqual(original, self.parser.ExpandStreet("Kuršių g.poriniai numeriai nuo Nr. 46 iki galo"))


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
        streetStr = "Panevėžys: Aldonos g.; Danutės g. neporiniai numeriai nuo Nr. 1 iki Nr. 27, poriniai numeriai nuo Nr. 2 iki Nr. 16; J. Tilvyčio g. neporiniai numeriai nuo Nr. 1 iki Nr. 35, poriniai numeriai nuo Nr. 2 iki Nr. 10; Katedros g., Katedros a.; Klaipėdos g. neporiniai numeriai nuo Nr. 3 iki Nr. 19; Krekenavos g. neporiniai numeriai nuo Nr. 1 iki galo; Nemuno g. poriniai numeriai nuo Nr. 2 iki Nr. 6; Nepriklausomybės a.; Ramygalos g. poriniai numeriai nuo Nr. 14 iki Nr. 50; S. Daukanto g. neporiniai numeriai nuo Nr. 39 iki Nr. 51; Sodų g., Vaižganto g., Varnaičių g.; Vysk. K. Paltaroko g. neporiniai numeriai nuo Nr. 1 iki galo; poriniai numeriai nuo Nr. 2 iki Nr. 16."

        parsed = list(self.parser.GetAddresses(streetStr))

        streets = ["Aldonos g.",
                   "Danutės g. neporiniai numeriai nuo Nr. 1 iki Nr. 27; poriniai numeriai nuo Nr. 2 iki Nr. 16",
                   "J. Tilvyčio g. neporiniai numeriai nuo Nr. 1 iki Nr. 35; poriniai numeriai nuo Nr. 2 iki Nr. 10",
                   "Katedros g.",
                   "Katedros a.",
                   "Klaipėdos g. neporiniai numeriai nuo Nr. 3 iki Nr. 19",
                   "Krekenavos g. neporiniai numeriai nuo Nr. 1 iki galo",
                   "Nemuno g. poriniai numeriai nuo Nr. 2 iki Nr. 6",
                   "Nepriklausomybės a.",
                   "Ramygalos g. poriniai numeriai nuo Nr. 14 iki Nr. 50",
                   "S. Daukanto g. neporiniai numeriai nuo Nr. 39 iki Nr. 51",
                   "Sodų g.",
                   "Vaižganto g.",
                   "Varnaičių g.",
                   "Vysk. K. Paltaroko g. neporiniai numeriai nuo Nr. 1 iki galo; poriniai numeriai nuo Nr. 2 iki Nr. 16."]

        for i in range(0, len(streets)):
            self.assertCity("Panevėžys", streets[i], parsed[i])

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
        streetStr = "Apušroto k., Biržų k., Bražiškių k., Dovydžių k., Dulbių k., Gembūčių k., Gerkiškių k., Kalnelio k., Karniškių k., Kruopių mstl., Laumėnų I k., Laumėnų II k., Liepkalnio k., Maušų k., Narbūčių k., Pagervių k. dalis, Pagervių k., Rudeliškių k., Saunorių I k., Saunorių II k., Senlaukio k., Spaigių k., Šiauliukų k., Šliupščių k., Vilkaičių k."
        parsed = list(self.parser.GetAddresses(streetStr))
        self.assertCity("Apušroto k.",      "", parsed[0])
        self.assertCity("Biržų k.",         "", parsed[1])
        self.assertCity("Bražiškių k.",     "", parsed[2])
        self.assertCity("Dovydžių k.",      "", parsed[3])
        self.assertCity("Dulbių k.",        "", parsed[4])
        self.assertCity("Gembūčių k.",      "", parsed[5])
        self.assertCity("Gerkiškių k.",     "", parsed[6])
        self.assertCity("Kalnelio k.",      "", parsed[7])
        self.assertCity("Karniškių k.",     "", parsed[8])
        self.assertCity("Kruopių mstl.",    "", parsed[9])
        self.assertCity("Laumėnų I k.",     "", parsed[10])
        self.assertCity("Laumėnų II k.",    "", parsed[11])
        self.assertCity("Liepkalnio k.",    "", parsed[12])
        self.assertCity("Maušų k.",         "", parsed[13])
        self.assertCity("Narbūčių k.",      "", parsed[14])
        self.assertCity("Pagervių k. dalis","", parsed[15])
        self.assertCity("Pagervių k.",      "", parsed[16])
        self.assertCity("Rudeliškių k.",    "", parsed[17])
        self.assertCity("Saunorių I k.",    "", parsed[18])
        self.assertCity("Saunorių II k.",   "", parsed[19])
        self.assertCity("Senlaukio k.",     "", parsed[20])
        self.assertCity("Spaigių k.",       "", parsed[21])
        self.assertCity("Šiauliukų k.",     "", parsed[22])
        self.assertCity("Šliupščių k.",     "", parsed[23])
        self.assertCity("Vilkaičių k.",     "", parsed[24])
        self.assertEqual(25, len(parsed))


    def assertCity(self, cityName, streetName, cityAddress):
        self.assertEqual(cityName, cityAddress.cityName)
        self.assertEqual(streetName, cityAddress.streetName)

    def test_Street_WithPoriniai(self):
        streetStr = "Naujoji Akmenė: Respublikos g. Nr. 19, Nr. 26, Nr. 28, numeriai nuo Nr. 1 iki Nr. 17; Respublikos a. Nr. 2."
        parsed = list(self.parser.GetAddresses(streetStr))
        self.assertCity("Naujoji Akmenė", "Respublikos g. Nr. 19; Nr. 26; Nr. 28; numeriai nuo Nr. 1 iki Nr. 17", parsed[0])
        self.assertCity("Naujoji Akmenė", "Respublikos a. Nr. 2.", parsed[1])
        self.assertEqual(2, len(parsed))

    def test_Street_WithHouseNumbers(self):
        streetStr = "Naujoji Akmenė: Respublikos g. Nr. 18, Nr. 20, Nr. 21, Nr. 23, Nr. 24, Nr. 25, Nr. 27; SB „Ąžuolas“, V. Kudirkos g."
        parsed = list(self.parser.GetAddresses(streetStr))
        self.assertCity("Naujoji Akmenė", "Respublikos g. Nr. 18; Nr. 20; Nr. 21; Nr. 23; Nr. 24; Nr. 25; Nr. 27", parsed[0])
        self.assertCity("Naujoji Akmenė", "SB „Ąžuolas“", parsed[1])
        self.assertCity("Naujoji Akmenė", "V. Kudirkos g.", parsed[2])
        self.assertEqual(3, len(parsed))



    def test_TwoCities(self):
        streetStr = "Gajauciškio k., Gemaitiškių k., Jurkionių k.: SB „Dzūkija“, Medukštos k., Navasiolkų k., Norgeliškių k., Padvariškių k., Panemuninkėlių k.; Panemuninkų k.: SB „Versmė“; Raganiškių k., Strielčių k., Taučionių k., Vaidaugų k., Vaisodžių k., Vaišupio k., Valiūnų k., Žiūkų k."
        parsed = list(self.parser.GetAddresses(streetStr))
        self.assertCity("Gajauciškio k.", "", parsed[0])
        self.assertCity("Gemaitiškių k.", "", parsed[1])
        self.assertCity("Jurkionių k.", "SB „Dzūkija“", parsed[2])
        self.assertCity("Medukštos k.", "", parsed[3])
        self.assertCity("Navasiolkų k.", "", parsed[4])
        self.assertCity("Norgeliškių k.", "", parsed[5])
        self.assertCity("Padvariškių k.", "", parsed[6] )
        self.assertCity("Panemuninkėlių k.", "", parsed[7])
        self.assertCity("Panemuninkų k.", "SB „Versmė“", parsed[8])
        self.assertCity("Raganiškių k.", "", parsed[9])
        self.assertCity("Strielčių k.", "", parsed[10])
        self.assertCity("Taučionių k.", "", parsed[11])
        self.assertCity("Vaidaugų k.", "", parsed[12]  )
        self.assertCity("Vaisodžių k.", "", parsed[13]  )
        self.assertCity("Vaišupio k.", "", parsed[14])
        self.assertCity("Valiūnų k.", "", parsed[15])
        self.assertCity("Žiūkų k.", "", parsed[16])
        self.assertEqual(17, len(parsed))

    def test_Villages_And_OneCity(self):
        streetStr = "Bažavos k., Kolonistų k.; Simnas: Alytaus g., Ateities g., Birutės g., Dariaus ir Girėno g., Draugystės g., Ežero g., Jaunimo g., Kaimynų g., Kreivoji g., Laisvės g., Melioratorių g., Naujoji g., Paupio g., Pavasario g., S. Nėries g., Saulėtekio g., Šviesos g., Taikos g., Vanagėlio g., Vytauto g., Žalioji g., Žemaitės g."

        parsed = list(self.parser.GetAddresses(streetStr))
        bazavos = parsed[0]
        kolonistu = parsed[1]
        simnasAlytaus = parsed[2]
        simnasAteities = parsed[3]
        simnasBirutes = parsed[4]
        self.assertCity("Bažavos k.", "", bazavos)
        self.assertCity("Kolonistų k.", "", kolonistu)
        self.assertCity("Simnas", "Alytaus g.", simnasAlytaus)
        self.assertCity("Simnas", "Ateities g.", simnasAteities)
        self.assertCity("Simnas", "Birutės g.", simnasBirutes)

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
