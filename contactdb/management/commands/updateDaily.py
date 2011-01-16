from django.core.management.base import BaseCommand
from pjutils.timemeasurement import TimeMeasurer
from pjutils.djangocommands import ExecManagementCommand

class Command(BaseCommand):
    args = '<>'
    help = 'Downloads documents from google docs, updates database'

    def handle(self, *args, **options):

        time = TimeMeasurer()
        imports = ["downloadDocs",
                   "importAll"]
        print "Will import following data:"
        for i in imports:
            print i

        print "Starting import"

        ExecManagementCommand(imports)

        print "finished. Took %s seconds" % time.ElapsedSeconds()
