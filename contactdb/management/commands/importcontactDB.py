from django.core.management.base import BaseCommand
from django.core import management
from pjutils.timemeasurement import TimeMeasurer


class Command(BaseCommand):
    args = '<>'
    help = 'Imports data to contact db database'



    def handle(self, *args, **options):
        
        time = TimeMeasurer()
        imports = ["importConstituencies", "importMPs", "importStreets"]

        print u"Will import followind data:"
        for i in imports: print i

        print u"Starting import"
        for i in imports:
            print u"importing %s" % (i)
            management.call_command(i)

        print u"finished importing ContactDB. Took %s seconds" % time.ElapsedSeconds()

            

        


