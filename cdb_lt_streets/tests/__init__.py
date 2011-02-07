from __future__ import absolute_import
from cdb_lt_streets.tests.TestAddressDeducer import TestAddressDeducer
from cdb_lt_streets.tests.TestHouseNumberUtils import TestContainsHouseNumbers
from cdb_lt_streets.tests.TestLTRegisterCenter import TestLTRegisterCenterLocations, TestLTRegisterCenterLinks, TestLTRegisterCenterOtherLinks
from cdb_lt_streets.tests.TestSearchInIndex import TestSearchInIndex, TestSearchCivilParishStreets_SingleStreet


__test__ = {
    'TestLTRegisterCenterLocations' : TestLTRegisterCenterLocations,
    'TestLTRegisterCenterLinks' : TestLTRegisterCenterLinks,
    'TestLTRegisterCenterOtherLinks' : TestLTRegisterCenterOtherLinks,
    'TestSearchInIndex': TestSearchInIndex,
    'TestAddressDeducer' : TestAddressDeducer,
    'TestContainsHouseNumbers' : TestContainsHouseNumbers,
    'TestSearchCivilParishStreets_SingleStreet' : TestSearchCivilParishStreets_SingleStreet
}
