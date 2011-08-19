from django.core.management.base import BaseCommand
from pjutils.timemeasurement import TimeMeasurer
from pjutils.djangocommands import ExecManagementCommand

class Command(BaseCommand):
    args = '<>'
    help = 'Imports data to contact db database'



    def handle(self, *args, **options):

        time = TimeMeasurer()
        imports = ["createMembers"]

        print "Will import following data:"
        for i in imports:
            print i

        ExecManagementCommand(imports)

        print u"finished importing members. Took %s seconds" % time.ElapsedSeconds()


