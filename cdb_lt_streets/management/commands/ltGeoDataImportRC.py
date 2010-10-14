#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from pjutils.timemeasurement import TimeMeasurer
from django.db import transaction
from parasykjiems.FeatureBroker.configs import defaultConfig
from urllib2 import urlopen
from pjutils.exc import ChainnedException
import time
from optparse import make_option
from cdb_lt_streets.LTRegisterCenter.webparser import RegisterCenterParser, LTGeoDataHierarchy
from cdb_lt_streets.LTRegisterCenter.mqbroker import LTRegisterQueue
from cdb_lt_streets.models import HierarchicalGeoData


class LTGeoDataImportException(ChainnedException):
    pass

class Command(BaseCommand):
    args = '<speed>'
    help = """Imports Geographical data for Lithuanian contact db from website http://www.registrucentras.lt/adr/p/index.php
\nThe data is not in geographic coordinates though, it is simply a hierarchical structure of districts / counties / cities / streets/ etc"""

    option_list = BaseCommand.option_list + (
        make_option('-d', '--max-depth',
            dest='max-depth',
            metavar="depth-level",
            default = "99",
            help='Specify a maximum depth-level to parse. Counts from root location, even though current url might be deep in hierarchy'),
        )


    def _SendPageMessagesLinks(self, page):
        count = 0
        for link in page.links:
            if (link.href is None):
                continue
            print "creating message for object '%s' " % (link)
            self.queue.SendMessage(link.href)
            count += 1
        return count

    def _SendPageMessagesOtherPages(self, page):
        count = 0
        for link in page.otherPages:
            if (link.href is None):
                continue
            # add links only on first page. So that we do not end up browsing through paged data forever
            if (link.text == "1"):
                break
            print "creating message for other page \n'%s' " % (link)
            self.queue.SendMessage(link.href)
            count += 1
        return count

    def SendPageMessages(self, page):
        count = 0
        """ Puts messages into queue for all additional links found in page"""
        l = len(page.location)
        if (l + 1> self.options['max-depth']):
            print "reaached max-depth level, will not send any messages for sub-urls"
        else:
            count += self._SendPageMessagesLinks(page)

        count += self._SendPageMessagesOtherPages(page)

        return count



    def _InsertLocationRows(self, page):
        insertedRows = 0
        parentLocationName = None
        parentLocationObject = None
        for location in page.location:

            parentLocationText = None
            if (parentLocationName is not None):
                parentLocationText = parentLocationName.text
            locationInDB = HierarchicalGeoData.FindByName(location.text, parentName = parentLocationText)

            if (locationInDB is None):
                # that means we have to create it
                locationInDB = self._CreateNewLocationObject(location.text, location.type, parentLocationObject)
                insertedRows += 1

            parentLocationName = location
            parentLocationObject = locationInDB
        return insertedRows

    def CreateRowIfNotExist(self, text, type, parentLocationText, parentLocationType):
        locationInDB = HierarchicalGeoData.FindByName(text, parentName = parentLocationText)
        if (locationInDB is not None):
            return
        try:
            parent = HierarchicalGeoData.objects.filter(name__contains = parentLocationText, type = parentLocationType)[0:1].get()
        except HierarchicalGeoData.DoesNotExist:
            raise LTGeoDataImportException("Could not find location with name '%s' and type '%s'" % (parentLocationText, parentLocationType))
        self._CreateNewLocationObject(text, type, parent)


    def _CreateNewLocationObject(self, text, type, parentLocationObject):
        locationInDB = HierarchicalGeoData()
        locationInDB.parent = parentLocationObject
        locationInDB.name = text
        locationInDB.type = type
        locationInDB.save()
        return locationInDB


    def _InsertContentRows(self, page):
        insertedRows = 0

        # extract location hierarchical type
        # Since page.location is a top-down hierarchy, so next element
        # will be the deeper element in hierarchy (at least in Lithuanian hierarhchy version)
        pageLocationLength = len(page.location)
        type = LTGeoDataHierarchy.Hierarchy[pageLocationLength]
        parentType = LTGeoDataHierarchy.Hierarchy[pageLocationLength - 1]
        parentName = page.location[len(page.location) -1].text

        parentLocationObject = HierarchicalGeoData.FindByName(name = parentName, type = parentType)
        if (parentLocationObject is None):
            raise LTGeoDataImportException("Could not find parent object by name %s and type " % (parentName, parentType) )

        for link in page.links:
            locationInDB = HierarchicalGeoData.FindByName(link.text, parentName = parentName)
            if (locationInDB is not None):
                continue
            # create new location object
            self._CreateNewLocationObject(link.text, type, parentLocationObject)
            insertedRows += 1


        return insertedRows


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

        insertedRows = 0

        insertedRows += self._InsertLocationRows(page)
        insertedRows += self._InsertContentRows(page)


        return insertedRows

    def CreateAdditionalGeoData(self):
        try:
            self.CreateRowIfNotExist(u"Palangos miesto seniūnija", HierarchicalGeoData.HierarchicalGeoDataType.CivilParish,
                u"Palangos miesto savivaldybė", HierarchicalGeoData.HierarchicalGeoDataType.Municipality)

            self.CreateRowIfNotExist(u"Šventosios seniūnija", HierarchicalGeoData.HierarchicalGeoDataType.CivilParish,
                u"Palangos miesto savivaldybė", HierarchicalGeoData.HierarchicalGeoDataType.Municipality)


            klaipedaCompanies = [u'Teritorija aptarnaujama UAB "Paslaugos būstui"',
                                 u'Teritorija aptarnaujama UAB "Vitės valdos"',
                                 u'Teritorija aptarnaujama UAB "Mūsų namų valdos"',
                                 u'Teritorija aptarnaujama UAB "Marių valdos"',
                                 u'Teritorija aptarnaujama UAB "Ąžuolyno valda"',
                                 u'Teritorija aptarnaujama UAB "Pempininkų valdos"',
                                 u'Teritorija aptarnaujama UAB "Debreceno valda"',
                                 u'Teritorija aptanaujama UAB "Buitis be rūpesčių"',
                                 u'Teritorija aptanaujama UAB "Vingio valdos"',
                                 u'Teritorija aptarnaujama UAB "Laukininkų valdos"']

            for company in klaipedaCompanies:
                self.CreateRowIfNotExist(company, HierarchicalGeoData.HierarchicalGeoDataType.CivilParish,
                    u"Klaipėdos miesto savivaldybė", HierarchicalGeoData.HierarchicalGeoDataType.Municipality)






        except (HierarchicalGeoData.DoesNotExist, LTGeoDataImportException):
            print u"Could not create addition geo data"
            print u"""This might happen if you have called with max-depth 1.  In that case appropriate data was simply
not created, so it is normal to receive HierarchicalGeoData.DoesNotExist exception. Please import
more data with at least max-depth 2"""
        

    def handle(self, *args, **options):

        print "Checking if MQ is empty"
        self.options = options
        self.options['max-depth'] = int(self.options['max-depth'])

        print u"max-depth is set to %d" % self.options['max-depth']

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

        print u"starting import procedure"

        elapsedTime = TimeMeasurer()
        lastMessageTime = elapsedTime.ElapsedSeconds()
        totalCreatedMessages = 0
        totalParsedMessages = 0
        totalInsertedRows = 0



        while (True):
            msg = self.queue.ReadMessage()
            if (msg is None):
                print u"no more messages, quitting"
                break

            # if timeDiff is greater than zero, then last message was processed
            # in longer time than requested,  so no sleep needed
            timeToProcessLastMessage = elapsedTime.ElapsedSeconds() - lastMessageTime
            throttleSpeed = 1 / throttleMessagesPerSecond
            timeDiff = timeToProcessLastMessage - throttleSpeed
            if (timeDiff < 0):
                toSleep = timeDiff * -1
                print u"will sleep for %s seconds" % toSleep
                time.sleep(toSleep)

            # reset the counter for this message
            lastMessageTime = elapsedTime.ElapsedSeconds()



            totalParsedMessages += 1

            self.queue.MQServer.BeginTransaction()
            url = msg.body
            print u"parsing url %s" % url

            response = urlopen(url)
            lines = "".join(response.readlines())

            pageParser = RegisterCenterParser(lines)
            page = pageParser.parse()

            # add external links as messages
            totalCreatedMessages += self.SendPageMessages(page)
            # create rows in database
            totalInsertedRows += self.CreateGeoRows(page)


            self.queue.ConsumeMessage(msg)
            self.queue.MQServer.Commit()
            print u"Created total %s additional messages. Inserted %s rows into db" % (totalCreatedMessages, totalInsertedRows)
            print u"Made %s requirests. Avg %s fetches per second" % (totalParsedMessages, totalParsedMessages / elapsedTime.ElapsedSeconds())

        print u"Took %s seconds" % elapsedTime.ElapsedSeconds()
        print u"Created total %s additional messages. Inserted %s rows into db" % (totalCreatedMessages, totalInsertedRows)
        print u"Made %s requirests. Avg %s fetches per second" % (totalParsedMessages, totalParsedMessages / elapsedTime.ElapsedSeconds())

        print u"Creating additional data, not availbe in www server"
        self.CreateAdditionalGeoData()
