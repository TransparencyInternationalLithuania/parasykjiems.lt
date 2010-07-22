from django.core.management.base import BaseCommand
from django.core import management
from pjutils.timemeasurement import TimeMeasurer
from django.db import transaction
from contactdb.models import HierarchicalGeoData
from parasykjiems.FeatureBroker.configs import defaultConfig
from contactdb.LTRegisterCenter.mqbroker import LTRegisterQueue
from contactdb.LTRegisterCenter.webparser import RegisterCenterParser, RegisterCenterPage
from urllib2 import urlopen
import time
import contactdb.models

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

    @transaction.commit_on_success
    def CreateGeoRows(self, page):
        # create all rows in database for given page.
        # A row is a hierarchical data node.
        # page object must be RegisterCenterPage object
        # page.locations refers to a hierarchical order where our new nodes will have to be put
        # page.links is an actual data which we will insert into databse.
        # page.links is a collection of LinkCell objects, so we will insert only the text part of it, not href

        # ensure all location objects are created in database
        #PollingDistrictStreet.objects.filter(electionDistrict = electionDistrict).delete()
        parentLocationName = None
        parentLocationObject = None
        for location in page.location:
            if (parentLocationName is not None):
                locationInDB = HierarchicalGeoData.objects.filter(parent__name = parentLocationName.text).filter(name = location.text)
            else:
                locationInDB = HierarchicalGeoData.objects.filter(name = location.text)
            try:
                locationInDB = locationInDB[0:1].get()
            except contactdb.models.HierarchicalGeoData.DoesNotExist:
                locationInDB = None

            if (locationInDB is None):
                # that means we have to create it
                locationInDB = HierarchicalGeoData()
                locationInDB.parent = parentLocationObject
                locationInDB.name = location.text
                locationInDB.type = location.type
                locationInDB.save()

            parentLocationName = location
            parentLocationObject = locationInDB

        

    def handle(self, *args, **options):

        print "Checking if MQ is empty"

        # by default every second will be fetched 1 message.
        # so it will be 1 url fetch per 1 second
        # usually you will want to set it to lower values, such as 0.5 (a url fetch in every 2 seconds)
        # or extremely slow 0.1 (in 10 seconds only 1 page fetch)
        # or maximum 2 (2 messages per second).
        throttleMessagesPerSecond = 1
        if (len(args) > 0):
            throttleMessagesPerSecond = float(args[0])


        self.queue = LTRegisterQueue()
        empty = self.queue.IsEmpty()
        if (empty):
            print "Queue is empty"
            print "Initialising import procedure"
            self.queue.InitialiseImport()

        print "starting import procedure"

        elapsedTime = TimeMeasurer()
        lastMessageTime = elapsedTime.ElapsedSeconds()
        totalCreatedMessages = 0
        totalParsedMessages = 0



        while (True):
            msg = self.queue.ReadMessage()
            if (msg is None):
                print "no more messages, quitting"
                break

            # if timeDiff is greater than zero, then last message was processed
            # in longer time than requested,  so no sleep needed
            timeToProcessLastMessage = elapsedTime.ElapsedSeconds() - lastMessageTime
            throttleSpeed = 1 / throttleMessagesPerSecond
            timeDiff = timeToProcessLastMessage - throttleSpeed
            if (timeDiff < 0):
                toSleep = timeDiff * -1
                print "will sleep for %s seconds" % toSleep
                time.sleep(toSleep)

            # reset the counter for this message
            lastMessageTime = elapsedTime.ElapsedSeconds()



            totalParsedMessages += 1

            self.queue.MQServer.BeginTransaction()
            url = msg.body
            print "parsing url %s" % url

            response = urlopen(url)
            lines = "".join(response.readlines())

            pageParser = RegisterCenterParser(lines)
            page = pageParser.parse()

            # add external links as messages
            totalCreatedMessages += self.SendPageMessages(page)
            # create rows in database
            self.CreateGeoRows(page)


            self.queue.ConsumeMessage(msg)
            self.queue.MQServer.Commit()
            print "Created total %s additional messages" % totalCreatedMessages
            print "Made %s requirests. Avg %s fetches per second" % (totalParsedMessages, totalParsedMessages / elapsedTime.ElapsedSeconds())

        print "Took %s seconds" % elapsedTime.ElapsedSeconds()
        print "Created total %s additional messages" % totalCreatedMessages
        print "Made %s requirests. Avg %s fetches per second" % (totalParsedMessages, totalParsedMessages / elapsedTime.ElapsedSeconds())
