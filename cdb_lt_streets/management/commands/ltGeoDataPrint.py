from django.core.management.base import BaseCommand
from django.core import management
from pjutils.MessagingServer.MessagingServer import MQServer
from pjutils.timemeasurement import TimeMeasurer
from cdb_lt_streets.LTRegisterCenter.mqbroker import LTRegisterQueue


class Command(BaseCommand):
    args = '<>'
    help = """Prints contents of queue"""


    def handle(self, *args, **options):

        print "Printing contents of queue"

        mqServer = MQServer()
        queue = LTRegisterQueue(mqServer=mqServer)

        if queue.IsEmpty():
            print "Queue is empty"
            return

        count = 0
        while True:
            msg = queue.ReadMessage()
            if msg is None:
                break;
            count +=1
            print msg.body

        print u"finished printing, total %s messages" % count

