from __future__ import absolute_import
from contactdb.tests.TestReadParliamentMembers import TestReadParliamentMembers
from contactdb.tests.TestImportLithuanianCounties import TestImportLithuanianCounties, TestLithuanianConstituencyParser
from contactdb.tests.TestAddressParser import TestAddressParser

__test__ = {
    'TestImportLithuanianCounties' : TestImportLithuanianCounties,
    'TestReadParliamentMembers' : TestReadParliamentMembers,
    'TestLithuanianCountyParser' : TestLithuanianConstituencyParser,
    'TestAddressParser' : TestAddressParser
}
