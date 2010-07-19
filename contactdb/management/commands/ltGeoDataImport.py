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


    def SendPageMessages(self, page):
        count = 0
        """ Puts messages into queue for all additional links found in page"""
        for link in page.links:
            if (link.href is None):
                continue
            print "creating message for object '%s' " % (link)
            self.queue.SendMessage(link.href)
            count += 1

        for link in page.otherPages:
            if (link.href is None):
                continue
            # add links only on first page. So that we dount end up browsing through paged data forever
            if (link.text == "1"):
                break
            print "creating message for other page \n'%s' " % (link)
            self.queue.SendMessage(link.href)
            count += 1

        return count


    def handle(self, *args, **options):

        print "Checking if MQ is empty"

        self.queue = LTRegisterQueue()
        empty = self.queue.IsEmpty()
        if (empty):
            print "Queue is empty"
            print "Initialising import procedure"
            self.queue.InitialiseImport()

        print "starting import procedure"

        time = TimeMeasurer()
        totalCreatedMessages = 0
        totalParsedMessages = 0
        while (True):
            msg = self.queue.ReadMessage()
            if (msg is None):
                print "no more messages, quitting"
                break

            totalParsedMessages += 1

            self.queue.MQServer.BeginTransaction()
            url = msg.body
            print "parsing url %s" % url

            response = urlopen(url)
            lines = "".join(response.readlines())

            pageParser = RegisterCenterParser(lines)
            page = pageParser.parse()

            totalCreatedMessages += self.SendPageMessages(page)


            #queue.ConsumeMessage(msg)
            self.queue.MQServer.Commit()

        print "Took %s seconds" % time.ElapsedSeconds()
        print "Created total %s additional messages" % totalCreatedMessages
        print "Made %s requirests. Avg %s fetches per second" % (totalParsedMessages, totalParsedMessages / time.ElapsedSeconds()) 
