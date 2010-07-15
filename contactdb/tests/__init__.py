from __future__ import absolute_import
from contactdb.tests.TestReadParliamentMembers import TestReadParliamentMembers
from contactdb.tests.TestImportLithuanianCounties import TestImportLithuanianCounties, TestLithuanianConstituencyParser
from contactdb.tests.TestAddressParser import TestAddressParser
from contactdb.tests.testLTRegisterCenter.TestLTRegisterCenter import TestLTRegisterCenter

__test__ = {
    'TestImportLithuanianCounties' : TestImportLithuanianCounties,
    'TestReadParliamentMembers' : TestReadParliamentMembers,
    'TestLithuanianConstituencyParser' : TestLithuanianConstituencyParser,
    'TestAddressParser' : TestAddressParser,
    'TestLTRegisterCenter' : TestLTRegisterCenter
}
