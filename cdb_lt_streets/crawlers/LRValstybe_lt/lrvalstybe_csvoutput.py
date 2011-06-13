#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
from cdb_lt_streets.crawlers.LRValstybe_lt.lrvalstybe_crawler import MunicipalityListReader, MunicipalityPageReader, CivilParishListReader, MunicipalityContactReader
import sys
from territories.stringUtils import stringIsIn

def convertToDict(c):
    """C is Contact class, and has standard contact properties
    Just puts them all in a dictionary
    """

    data = {}
    data[u"title"] = c.title
    data[u"fullname"] = c.name
    data[u"email"] = c.email
    data[u"officephone"] = c.phone
    data[u"officeaddress"] = c.address
    if c.room is not None:
        data[u"officeaddress"] = u"%s. Kabinetas %s" % (c.address, c.room)
    return data

def yieldCivilParishHeadMembers():
    for c in yieldCivilParishContacts():    
        if stringIsIn(c[u"title"], [u"seniūnas", u"seniūnė"]):
            yield c

def yieldCivilParishContacts():
    """ crawls lrvalstybe.lt page, and returns a dictionary populated with data for each civil parish contact.
    This includes all possible contact
    """
    data = {}

    crawler = MunicipalityListReader(u"http://www.lrvalstybe.lt/savivaldybes-4906/")
    for municipalityName, municipalityUrl in list(crawler.getMunicipalityList()):
        data[u"municipality"] = municipalityName
        reader = MunicipalityPageReader(municipalityUrl)
        civilParishText, civilParishUrl =  reader.getCivilParishListUrl()

        for parish, url in CivilParishListReader(municipalityUrl, civilParishUrl).getCivilParishList():
            data[u"civilparish"] = parish
            data[u"comments"] = url

            if url is None:
                continue
            reader = MunicipalityContactReader(url)
            for c in reader.getContactList():
                #convert contact to dictionary
                clientDict = convertToDict(c)
                # add municipality and other data
                clientDict.update(data)
                yield clientDict

class LRValstybeCsvOut:
    """ Prints out contacts as csv lines.  Contacts are fetched from lrvalstybe.lt website """

    def __init__(self, outStream = sys.stdout, headers = None):
        self.stream = outStream
        self.headers = headers
        self.formatRow = u",".join(['"%s"' for k in headers])

    def printSingleContact(self, contact):

        # we are not usin dict writer here, as it is writing an empty new line on win32 for some reason
        #file = csv.DictWriter(sys.stdout, headers)
        #headersRow = dict( (n,n) for n in headers )
        #file.writerow(headersRow)

        # we are not usin dict writer here, as it is writing an empty new line on win32 for some reason
        """# get only fields, that are supported in headers
        d = dict( (key, civilParishMember[key] if civilParishMember.has_key(key) else u"") for key in headers)
        # convert to utf-8
        d = dict( (k, v.encode('utf-8') if isinstance(v, unicode) else v) for k, v in d.iteritems())
        file.writerow(d)
"""

        values = [contact[h] if contact.has_key(h) else None for h in self.headers]
        values = [u"" if v is None else v for v in values]
        row = self.formatRow % tuple(values)
        print row

    def writeHeader(self):
        print u",".join(self.headers)


"""
def printCivilParish():

    headers = [u"fullname", u"email", u"municipality", u"civilparish", u"officephone", u"officeaddress", u"title", u"comments"]

    # we are not usin dict writer here, as it is writing an empty new line on win32 for some reason
    #file = csv.DictWriter(sys.stdout, headers)
    #headersRow = dict( (n,n) for n in headers )
    #file.writerow(headersRow)

    print u", ".join(headers)
    formatRow = u",".join(['"%s"' for k in headers])

    for civilParishMember in yieldCivilParish():
        # we are not usin dict writer here, as it is writing an empty new line on win32 for some reason
        values = [civilParishMember[h] if civilParishMember.has_key(h) else None for h in headers]
        row = formatRow % tuple(values)
        print row
"""

def yieldMayorsOnly():
    for c in yieldMayorAdministartionWorkers():
        if stringIsIn(c[u"title"], [u"meras", u"merė"]):
            yield c

def yieldMayorAdministartionWorkers():
    """ crawls lrvalstybe.lt page, and returns dictionary with mayor data"""
    data = {}
    crawler = MunicipalityListReader(u"http://www.lrvalstybe.lt/savivaldybes-4906/")
    for municipalityName, municipalityUrl in list(crawler.getMunicipalityList()):
        data[u"municipality"] = municipalityName

        reader = MunicipalityPageReader(municipalityUrl)
        mayorText, mayorUrl = reader.getMayorUrl()
        reader = MunicipalityContactReader(mayorUrl)
        data[u"comments"] = mayorUrl
        for c in reader.getContactList():
            #convert contact to dictionary
            clientDict = convertToDict(c)
            # add municipality and other data
            clientDict.update(data)
            yield clientDict