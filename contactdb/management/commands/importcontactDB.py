from django.core.management.base import BaseCommand
from django.core import management


class Command(BaseCommand):
    args = '<>'
    help = 'Imports data to contact db database'



    def handle(self, *args, **options):
        

        imports = ["importCounties", "importMPs", "importStreets"]

        print "Will import followind data:"
        for i in imports: print i

        print "Starting import"
        for i in imports:
            print "importing %s" % (i)
            management.call_command(i)

        print "finished importing ContactDB"

            

        


