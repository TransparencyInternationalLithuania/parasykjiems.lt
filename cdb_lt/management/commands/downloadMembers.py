from django.core.management.base import BaseCommand
from cdb_lt.management.commands.createMembers import ImportSourcesMembers
from cdb_lt.management.commands.importSources import GoogleDocsMemberSources
from pjutils.args.Args import ExtractRange
from pjutils.gdocsUtils import GoogleDocsLogin, downloadDoc
from settings import *
from pjutils.timemeasurement import TimeMeasurer
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    args = '<>'
    help = 'Download a google docs document to specific location'

    def handle(self, *args, **options):
        """ Downloads documents as csv (tab-delimited) files from google docs"""

        fromNumber = 0
        toNumber = None

        allDocs = [(GoogleDocsMemberSources.LithuanianMPs, ImportSourcesMembers.LithuanianMPs),
                (GoogleDocsMemberSources.LithuanianCivilParishMembers, ImportSourcesMembers.LithuanianCivilParishMembers),
                (GoogleDocsMemberSources.LithuanianMunicipalityMembers, ImportSourcesMembers.LithuanianMunicipalityMembers),
                (GoogleDocsMemberSources.LithuanianSeniunaitijaMembers, ImportSourcesMembers.LithuanianSeniunaitijaMembers),
        ]
        
        if len(args) >= 1:
            fromNumber, toNumber = ExtractRange(args[0])
        if toNumber is None:
            toNumber = len(allDocs)

        elapsedTime = TimeMeasurer()
        print "Will download docs from %s to %s " % (fromNumber, toNumber)
        login = GoogleDocsLogin(GlobalSettings.GOOGLE_DOCS_USER, GlobalSettings.GOOGLE_DOCS_PASSWORD)
        for docSource, importSource in allDocs[fromNumber:toNumber]:
            downloadDoc(login, docSource, importSource)

        print u"Took %s seconds" % elapsedTime.ElapsedSeconds()