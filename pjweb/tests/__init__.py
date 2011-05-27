from __future__ import absolute_import
from pjweb.tests.testFirstPage import TestFirstPage
from pjweb.tests.testTerritoryPlugin.testSubmitSingleQuery import TestUserEntersAddress, TestDisplayMembersFromStreet
from pjweb.tests.writeToRepresentative.writeToSingleRepr import TestWriteToSingleRepr, TestWriteToSingleRepr_NoEmail
from pjweb.tests.email.testRenderMailTemplates import TestRenderAllEmailTemplates_InEveryLanguage

__test__ = {
    'TestFirstPage' : TestFirstPage,
    # testTerritoryPlugin
    'TestUserEntersAddress' : TestUserEntersAddress,
    'TestDisplayMembersFromStreet' : TestDisplayMembersFromStreet,

    # write to representative
    'TestWriteToSingleRepr' : TestWriteToSingleRepr,
    'TestWriteToSingleRepr_NoEmail' : TestWriteToSingleRepr_NoEmail,

    # email
    'TestRenderAllEmailTemplates_InEveryLanguage' : TestRenderAllEmailTemplates_InEveryLanguage
}
