from __future__ import absolute_import
from cdb_lt_streets.tests.TestAddressDeducer import TestAddressDeducer
from cdb_lt_streets.tests.TestHouseNumberUtils import TestContainsHouseNumbers
from cdb_lt_streets.tests.TestLTRegisterCenter import TestLTRegisterCenterLocations, TestLTRegisterCenterLinks, TestLTRegisterCenterOtherLinks
from cdb_lt_streets.tests.TestSearchInIndex import TestSearchInIndex, TestSearchCivilParishStreets_SingleStreet, TestSearchInstitutionStreets_WithStreetAndHouseNumber, TestSearchInstitutionStreets_SingleRepresentative


__test__ = {
    'TestLTRegisterCenterLocations' : TestLTRegisterCenterLocations,
    'TestLTRegisterCenterLinks' : TestLTRegisterCenterLinks,
    'TestLTRegisterCenterOtherLinks' : TestLTRegisterCenterOtherLinks,
    'TestSearchInIndex': TestSearchInIndex,
    'TestAddressDeducer' : TestAddressDeducer,
    'TestContainsHouseNumbers' : TestContainsHouseNumbers,
    'TestSearchCivilParishStreets_SingleStreet' : TestSearchCivilParishStreets_SingleStreet,
    'TestSearchInstitutionStreets_WithStreetAndHouseNumber' : TestSearchInstitutionStreets_WithStreetAndHouseNumber,
    'TestSearchInstitutionStreets_SingleRepresentative': TestSearchInstitutionStreets_SingleRepresentative
}
