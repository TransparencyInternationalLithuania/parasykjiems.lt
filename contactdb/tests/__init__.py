from __future__ import absolute_import
from contactdb.tests.TestReadParliamentMembers import TestReadParliamentMembers
from contactdb.tests.TestImportLithuanianCounties import TestImportLithuanianCounties, TestLithuanianCountyParser

__test__ = {
    'TestImportLithuanianCounties' : TestImportLithuanianCounties,
    'TestReadParliamentMembers' : TestReadParliamentMembers,
    'TestLithuanianCountyParser' : TestLithuanianCountyParser
}
