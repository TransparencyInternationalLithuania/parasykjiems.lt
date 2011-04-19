from __future__ import absolute_import
from territories.tests.InstitutionIndexes.TestInstitutionIndexes import TestSearchCivilParishStreets_SingleStreet, TestSearchInstitutionStreets_WithStreetAndHouseNumber, TestSearchInstitutionStreets_SingleRepresentative, TestSearchInstitutionStreets_ArminuKaimas, TestSearchInstitutionStreets_NumberToIsNone, TestSearchInstitutionStreets_NumberWithLetter, TestSearchInstitutionStreets_DifferentTypesOfInstitutions, TestSearchInstitutionStreets_DifferentTypesOfInstitutionsMPAndMayor, TestSearchInstitutionStreets_IssuesWithCivilParish, TestSearchInstitutionStreets_IssuesWithCivilParish_MultipleCivPar, TestSearchInstitutionStreets_StreetNamesWithDots
from territories.tests.TestAddressDeducer import TestAddressDeducer
from territories.tests.TestHouseNumberUtils import TestContainsHouseNumbers, TestPadHouseNumberWithZeroes, TestIsHouseNumberOdd
from territories.tests.TestLTRegisterCenter import TestLTRegisterCenterLocations, TestLTRegisterCenterLinks, TestLTRegisterCenterOtherLinks
from territories.tests.TestStreetUtils import TestExtractStreetEndingForm, TestChangeDoubleWordStreetToDot
from territories.tests.ltStreetIndexes.testLtStreetIndexes import TestSearchLtStreetIndex_SingleStreet, TestSearchLtStreetIndex_StreetsWithNumbersInName, TestSearchLtStreetIndex_DifferentEndings, TestSearchLtStreetIndex_StreetDoubleWordAndLithuanianLetter, TestSearchLtStreetIndex_Village, TestSearchLtStreetIndex_StreetDoubleWord_WithDot
from territories.tests.testYieldHouseRanges import TestYieldHouseRanges


__test__ = {
    'TestYieldHouseRanges' : TestYieldHouseRanges,
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
    'TestSearchLtStreetIndex_DifferentEndings' : TestSearchLtStreetIndex_DifferentEndings,
    'TestSearchLtStreetIndex_StreetDoubleWordAndLithuanianLetter' : TestSearchLtStreetIndex_StreetDoubleWordAndLithuanianLetter,
    'TestSearchLtStreetIndex_Village': TestSearchLtStreetIndex_Village,
    'TestSearchInstitutionStreets_DifferentTypesOfInstitutions' : TestSearchInstitutionStreets_DifferentTypesOfInstitutions,
    'TestSearchInstitutionStreets_DifferentTypesOfInstitutionsMPAndMayor' : TestSearchInstitutionStreets_DifferentTypesOfInstitutionsMPAndMayor,
    'TestSearchInstitutionStreets_IssuesWithCivilParish' : TestSearchInstitutionStreets_IssuesWithCivilParish,
    'TestSearchInstitutionStreets_IssuesWithCivilParish_MultipleCivPar' : TestSearchInstitutionStreets_IssuesWithCivilParish_MultipleCivPar,
    'TestSearchInstitutionStreets_StreetNamesWithDots' : TestSearchInstitutionStreets_StreetNamesWithDots,
    'TestChangeDoubleWordStreetToDot' : TestChangeDoubleWordStreetToDot,
    'TestSearchLtStreetIndex_StreetDoubleWord_WithDot' : TestSearchLtStreetIndex_StreetDoubleWord_WithDot
}
