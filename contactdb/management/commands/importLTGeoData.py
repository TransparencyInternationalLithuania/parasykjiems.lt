from django.core.management.base import BaseCommand
from django.core import management
from pjutils.timemeasurement import TimeMeasurer
from parasykjiems.FeatureBroker.configs import defaultConfig
from contactdb.LTRegisterCenter.mqbroker import LTRegisterQueue
from contactdb.LTRegisterCenter.webparser import RegisterCenterParser, RegisterCenterPage

from urllib2 import urlopen

class Command(BaseCommand):
    args = '<>'
    help = """Imports Geographical data for Lithuanian contact db from website http://www.registrucentras.lt/adr/p/index.php
\nThe data is not in geographic coordinates though, it is simply a hierarchical structure of districts / counties / cities / streets/ etc"""



    def handle(self, *args, **options):

        print "Checking if MQ is empty"

        queue = LTRegisterQueue()
        empty = queue.IsEmpty()
        if (empty):
            print "Queue is empty"
            print "Initialising import procedure"
            queue.InitialiseImport()

        print "starting import procedure"

        msgCount = 0

        while (True):
            msg = queue.ReadMessage()
            if (msg is None):
                print "no more messages, quitting"
                break


            msgCount += 1
            if (msgCount > 2):
                print "maximum 2 messages can be processed"
                break

            
            queue.MQServer.BeginTransaction()
            url = msg.body
            print "parsing url %s" % url

            response = urlopen(url)
            lines = "".join(response.readlines())

            pageParser = RegisterCenterParser(lines)
            page = pageParser.parse()

            for link in page.links:
                print "creating message for object '%s' " % (link)
                queue.SendMessage(link.href)

            queue.ConsumeMessage(msg)
            queue.MQServer.Commit()
