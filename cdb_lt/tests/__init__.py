from __future__ import absolute_import
from cdb_lt.tests.mpStreetReaderTests.TestImportLithuanianCounties import TestImportLithuanianCounties
from cdb_lt.tests.mpStreetReaderTests.TestParseConstituencies import TestPollingDistrictStreetExpander, TestLithuanianConstituencyParser, TestAddressParser
from cdb_lt.tests.seniunaitijaTerritoryReaderTests.TestSeniunaitijaAddressExpander import TestSeniunaitijaAddressExpander
from cdb_lt.tests.testPersonUtils import TestSpitFullName

__test__ = {
    'TestPollingDistrictStreetExpander' : TestPollingDistrictStreetExpander,
    'TestImportLithuanianCounties' : TestImportLithuanianCounties,
    'TestLithuanianConstituencyParser' : TestLithuanianConstituencyParser,
    'TestAddressParser' : TestAddressParser,
    'TestSeniunaitijaAddressExpander' : TestSeniunaitijaAddressExpander,
    'TestSpitFullName' : TestSpitFullName
}
