from django.core.management.base import BaseCommand
from django.core import management
from pjutils.timemeasurement import TimeMeasurer
from parasykjiems.FeatureBroker.configs import defaultConfig
from cdb_lt_streets.LTRegisterCenter.mqbroker import LTRegisterQueue


class Command(BaseCommand):
    args = '<>'
    help = """Imports Geographical data for Lithuanian contact db from website http://www.registrucentras.lt/adr/p/index.php
\nThe data is not in geographic coordinates though, it is simply a hierarchical structure of districts / counties / cities / streets/ etc"""



    def handle(self, *args, **options):

        print u"Clearing queue from any messages that were left unprocessed"

        queue = LTRegisterQueue()
        if (queue.IsEmpty()):
            print u"queue is already empty"
            return
            
        queue.Clear()
        print u"queue has been cleared"