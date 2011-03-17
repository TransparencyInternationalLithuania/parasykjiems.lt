from __future__ import absolute_import
from pjweb.tests.testFirstPage import TestFirstPage
from pjweb.tests.testTerritoryPlugin.testSubmitSingleQuery import TestUserEntersAddress, TestDisplayMembersFromStreet

__test__ = {
    'TestFirstPage' : TestFirstPage,
    # testTerritoryPlugin
    'TestUserEntersAddress' : TestUserEntersAddress,
    'TestDisplayMembersFromStreet' : TestDisplayMembersFromStreet
}
