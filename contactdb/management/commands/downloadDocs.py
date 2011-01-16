from django.core.management.base import BaseCommand
from django.db import transaction
from contactdb.gdocs import SpreadSheetClient, GoogleDocsLogin
from settings import *
import csv
import pjutils.uniconsole
from contactdb.imp import GoogleDocsSources, ImportSources
import os
from cdb_lt_streets.management.commands.ltGeoDataImportCsv import ltGeoDataSources
import gdata
from pjutils.deprecated import deprecated
from pjutils.timemeasurement import TimeMeasurer
from cdb_lt_streets.management.commands.ltGeoDataCrawl import ExtractRange

logger = logging.getLogger(__name__)





class Command(BaseCommand):
    args = '<>'
    help = 'Download a google docs document to specific location'

    def handle(self, *args, **options):
        """ Downloads documents as csv (tab-delimited) files from google docs"""

        fromNumber = 0
        toNumber = None

        allDocs = [(GoogleDocsSources.LithuanianMPs, ImportSources.LithuanianMPs),
                (GoogleDocsSources.LithuanianCivilParishMembers, ImportSources.LithuanianCivilParishMembers),
                (GoogleDocsSources.LithuanianMunicipalityMembers, ImportSources.LithuanianMunicipalityMembers),
                (GoogleDocsSources.LithuanianSeniunaitijaMembers, ImportSources.LithuanianSeniunaitijaMembers),
                (GoogleDocsSources.LithuanianMunicipalities, ImportSources.LithuanianMunicipalities),
                (GoogleDocsSources.LithuanianCivilParishes, ImportSources.LithuanianCivilParishes)

        ]
        if (len(args) >= 1):
            fromNumber, toNumber = ExtractRange(args[0])
        if (toNumber is None):
            toNumber = len(allDocs)

        elapsedTime = TimeMeasurer()
        print "Will download docs from %s to %s " % (fromNumber, toNumber)
        login = GoogleDocsLogin(GlobalSettings.GOOGLE_DOCS_USER, GlobalSettings.GOOGLE_DOCS_PASSWORD)
        for docSource, importSource in allDocs[fromNumber:toNumber]:
            downloadDoc(login, docSource, importSource)

        print u"Took %s seconds" % elapsedTime.ElapsedSeconds()