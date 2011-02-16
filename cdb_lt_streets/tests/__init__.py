from __future__ import absolute_import
from cdb_lt_streets.tests.InstitutionIndexes.TestInstitutionIndexes import TestSearchCivilParishStreets_SingleStreet, TestSearchInstitutionStreets_WithStreetAndHouseNumber, TestSearchInstitutionStreets_SingleRepresentative, TestSearchInstitutionStreets_ArminuKaimas, TestSearchInstitutionStreets_NumberToIsNone, TestSearchInstitutionStreets_NumberWithLetter
from cdb_lt_streets.tests.TestAddressDeducer import TestAddressDeducer
from cdb_lt_streets.tests.TestHouseNumberUtils import TestContainsHouseNumbers, TestPadHouseNumberWithZeroes, TestIsHouseNumberOdd
from cdb_lt_streets.tests.TestLTRegisterCenter import TestLTRegisterCenterLocations, TestLTRegisterCenterLinks, TestLTRegisterCenterOtherLinks
from cdb_lt_streets.tests.TestStreetUtils import TestExtractStreetEndingForm
from cdb_lt_streets.tests.ltStreetIndexes.testLtStreetIndexes import TestSearchLtStreetIndex_SingleStreet, TestSearchLtStreetIndex_StreetsWithNumbersInName, TestSearchLtStreetIndex_DifferentEndings


__test__ = {
    'TestLTRegisterCenterLocations' : TestLTRegisterCenterLocations,
    'TestLTRegisterCenterLinks' : TestLTRegisterCenterLinks,
    'TestLTRegisterCenterOtherLinks' : TestLTRegisterCenterOtherLinks,
    'TestExtractStreetEndingForm': TestExtractStreetEndingForm,
    'TestAddressDeducer' : TestAddressDeducer,
    'TestContainsHouseNumbers' : TestContainsHouseNumbers,
    'TestSearchCivilParishStreets_SingleStreet' : TestSearchCivilParishStreets_SingleStreet,
    'TestSearchInstitutionStreets_WithStreetAndHouseNumber' : TestSearchInstitutionStreets_WithStreetAndHouseNumber,
    'TestSearchInstitutionStreets_SingleRepresentative': TestSearchInstitutionStreets_SingleRepresentative,
    'TestSearchLtStreetIndex_SingleStreet' : TestSearchLtStreetIndex_SingleStreet,
    'TestSearchLtStreetIndex_StreetsWithNumbersInName': TestSearchLtStreetIndex_StreetsWithNumbersInName,
    'TestSearchInstitutionStreets_ArminuKaimas' : TestSearchInstitutionStreets_ArminuKaimas,
    'TestSearchInstitutionStreets_NumberToIsNone' : TestSearchInstitutionStreets_NumberToIsNone,
    'TestPadHouseNumberWithZeroes' : TestPadHouseNumberWithZeroes,
    'TestSearchInstitutionStreets_NumberWithLetter' : TestSearchInstitutionStreets_NumberWithLetter,
    'TestIsHouseNumberOdd': TestIsHouseNumberOdd,
    'TestSearchLtStreetIndex_DifferentEndings' : TestSearchLtStreetIndex_DifferentEndings
}
