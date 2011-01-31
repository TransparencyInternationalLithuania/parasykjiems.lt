from django.core.management.base import BaseCommand
from django.core import management
from pjutils.timemeasurement import TimeMeasurer
from parasykjiems.FeatureBroker.configs import defaultConfig
from cdb_lt_streets.LTRegisterCenter.mqbroker import LTRegisterQueue
from cdb_lt_streets.models import HierarchicalGeoData
from cdb_lt_streets.management.commands.ltGeoDataImportRC import LTGeoDataImportException


class Command(BaseCommand):
    args = '<>'
    help = """Prints contents of queue"""


    def handle(self, *args, **options):

        self.CreateAdditionalGeoData()


    def CreateRowIfNotExist(self, text, type, parentLocationText, parentLocationType):
        locationInDB = HierarchicalGeoData.FindByName(text, parentName = parentLocationText)
        if (locationInDB is not None):
            return
        try:
            parent = HierarchicalGeoData.objects.filter(name__contains = parentLocationText, type = parentLocationType)[0:1].get()
        except HierarchicalGeoData.DoesNotExist:
            raise LTGeoDataImportException("Could not find location with name '%s' and type '%s'" % (parentLocationText, parentLocationType))
        self._CreateNewLocationObject(text, type, parent)

    def CreateAdditionalGeoData(self):
            try:
                self.CreateRowIfNotExist(u"Palangos miesto seniūnija", HierarchicalGeoData.HierarchicalGeoDataType.CivilParish,
                    u"Palangos miesto savivaldybė", HierarchicalGeoData.HierarchicalGeoDataType.Municipality)

                self.CreateRowIfNotExist(u"Šventosios seniūnija", HierarchicalGeoData.HierarchicalGeoDataType.CivilParish,
                    u"Palangos miesto savivaldybė", HierarchicalGeoData.HierarchicalGeoDataType.Municipality)


                klaipedaCompanies = [u'Teritorija aptarnaujama UAB "Paslaugos būstui"',
                                     u'Teritorija aptarnaujama UAB "Vitės valdos"',
                                     u'Teritorija aptarnaujama UAB "Mūsų namų valdos"',
                                     u'Teritorija aptarnaujama UAB "Marių valdos"',
                                     u'Teritorija aptarnaujama UAB "Ąžuolyno valda"',
                                     u'Teritorija aptarnaujama UAB "Pempininkų valdos"',
                                     u'Teritorija aptarnaujama UAB "Debreceno valda"',
                                     u'Teritorija aptanaujama UAB "Buitis be rūpesčių"',
                                     u'Teritorija aptanaujama UAB "Vingio valdos"',
                                     u'Teritorija aptarnaujama UAB "Laukininkų valdos"']

                for company in klaipedaCompanies:
                    self.CreateRowIfNotExist(company, HierarchicalGeoData.HierarchicalGeoDataType.CivilParish,
                        u"Klaipėdos miesto savivaldybė", HierarchicalGeoData.HierarchicalGeoDataType.Municipality)






            except (HierarchicalGeoData.DoesNotExist, LTGeoDataImportException):
                print u"Could not create addition geo data"
                print u"""This might happen if you have called with max-depth 1.  In that case appropriate data was simply
    not created, so it is normal to receive HierarchicalGeoData.DoesNotExist exception. Please import
    more data with at least max-depth 2"""

