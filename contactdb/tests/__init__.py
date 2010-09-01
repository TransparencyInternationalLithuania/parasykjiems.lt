from __future__ import absolute_import
from contactdb.tests.TestReadParliamentMembers import TestReadParliamentMembers
from contactdb.tests.TestImportLithuanianCounties import TestImportLithuanianCounties, TestLithuanianConstituencyParser, TestSeniunaitijaStreetParser
from contactdb.tests.TestAddressParser import TestAddressParser, TestPollingDistrictStreetExpander, TestSeniunaitijaAddressExpander
from contactdb.tests.testLTRegisterCenter.TestLTRegisterCenter import TestLTRegisterCenterLocations, TestLTRegisterCenterLinks, TestLTRegisterCenterOtherLinks

__test__ = {
    'TestImportLithuanianCounties' : TestImportLithuanianCounties,
    'TestReadParliamentMembers' : TestReadParliamentMembers,
    'TestLithuanianConstituencyParser' : TestLithuanianConstituencyParser,
    'TestAddressParser' : TestAddressParser,
    'TestLTRegisterCenterLocations' : TestLTRegisterCenterLocations,
    'TestLTRegisterCenterLinks' : TestLTRegisterCenterLinks,
    'TestLTRegisterCenterOtherLinks' : TestLTRegisterCenterOtherLinks,
    'TestSeniunaitijaStreetParser' : TestSeniunaitijaStreetParser,
    'TestPollingDistrictStreetExpander' : TestPollingDistrictStreetExpander,
    'TestSeniunaitijaAddressExpander' : TestSeniunaitijaAddressExpander
}
