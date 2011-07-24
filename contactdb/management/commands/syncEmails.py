from django.core.management.base import BaseCommand
from cdb_lt.personUtils import splitIntoNameAndSurname
from contactdb.models import PersonPosition
from pjutils.timemeasurement import TimeMeasurer
from pjweb.models import Email
from pjutils.djangocommands import ExecManagementCommand

class Command(BaseCommand):
    args = '<>'
    help = """Syncs emails to PersonPosition objects, since these might go out of sync, if you clear members,
    and then import them again"""



    def handle(self, *args, **options):

        time = TimeMeasurer()

        for e in Email.objects.all().filter(msg_type__exact = 'Question'):
            print e.recipient_name
            name, surname = splitIntoNameAndSurname(e.recipient_name)
            personPosition = PersonPosition.objects.filter(person__name = name).filter(person__surname=surname)\
                .filter(email = e.recipient_mail)
            try:
                pp = personPosition.get()
            except PersonPosition.DoesNotExist:
                continue

            e.recipient_id = pp.id
            e.save()

        print u"finished importing members. Took %s seconds" % time.ElapsedSeconds()


