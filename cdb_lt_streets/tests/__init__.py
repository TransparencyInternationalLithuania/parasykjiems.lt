from __future__ import absolute_import
from cdb_lt_streets.tests.TestLTRegisterCenter import TestLTRegisterCenterLocations, TestLTRegisterCenterLinks, TestLTRegisterCenterOtherLinks
from cdb_lt_streets.tests.TestSearchInIndex import TestSearchInIndex, TestAddressDeducer


__test__ = {
    'TestLTRegisterCenterLocations' : TestLTRegisterCenterLocations,
    'TestLTRegisterCenterLinks' : TestLTRegisterCenterLinks,
    'TestLTRegisterCenterOtherLinks' : TestLTRegisterCenterOtherLinks,
    'TestSearchInIndex': TestSearchInIndex,
    'TestAddressDeducer' : TestAddressDeducer
}
