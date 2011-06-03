#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ClientForm import ParseResponse
from BeautifulSoup import BeautifulSoup, NavigableString
import re
from urllib2 import urlopen
from pjutils.exc import ChainnedException

class LrValstybeCrawlerException(ChainnedException):
    pass


def readUrl(url):
    """ constructs a BeautifulSoup instance for a web page defined by url"""
    response = urlopen(url)
    htmlText = "".join(response.readlines())
    htmlText = unicode(htmlText, "utf-8")
    return BeautifulSoup(htmlText)

def extractTextAndUrl(ahrefTag):
    text = ahrefTag.text
    url = ahrefTag.attrs[0][1]
    return text, url

def findAhrefTag(soupForm, linkText):
    link = soupForm.find(text=re.compile(linkText))
    if link.parent.name != u"a":
        return None
    return link.parent

class MunicipalityPageReader:

    def __init__(self, municipalityUrl):
        self.url = municipalityUrl
        self.soupForm = readUrl(municipalityUrl)
        pass



    def getMayorUrl(self):
        """ reads municipality page, and returns url with mayor info.
        example: municipalityUrl: http://www.lrvalstybe.lt/akmenes-rajono-savivaldybe-4907/
        result: http://www.lrvalstybe.lt/meras-999705/
        """
        vadovybeHRefTag = findAhrefTag(self.soupForm, u"Vadovybė")
        url = extractTextAndUrl(vadovybeHRefTag)[1]
        vadovybeUrl = "%s%s" % ("http://www.lrvalstybe.lt/", url)

        # some pages will not contain link to mayor, but will instead immediatelly have mayor inside
        # compare this page http://www.lrvalstybe.lt//vadovybe-5089/
        # and this page: http://www.lrvalstybe.lt/vadovybe-4946/

        #mayorForm.find("div", "contact")

        mayorForm = readUrl(vadovybeUrl)
        mayorHRefTag = findAhrefTag(mayorForm, u"Meras|Merė|meras|merė")
        if mayorHRefTag is None:
            return u"Meras", url
        return extractTextAndUrl(mayorHRefTag)


class Contact:
    pass

def getFieldNotEmpty(element, elementType = None, cssClass = None, textToSearch = None, doubleNext = False):
    d = None
    if cssClass is not None:
        d = element.find(elementType, cssClass)
    elif textToSearch is not None:
        d = element.find(text = re.compile(textToSearch))
    if d is None:
        return None

    if doubleNext is False:
        return d.next
    return d.next.next


class MunicipalityContactReader:
    def __init__(self, url):
        self.soupForm = readUrl(url)
        self.url = url

    def extractContact(self, div):
        c = Contact()
        c.name = getFieldNotEmpty(div, elementType="div", cssClass="con_name", doubleNext = True)
        c.title = getFieldNotEmpty(div, elementType="div", cssClass="con_title", doubleNext = False)
        c.address = getFieldNotEmpty(div, textToSearch = u"Adresas")
        c.room = getFieldNotEmpty(div, textToSearch = u"Kabinetas")
        c.phone = getFieldNotEmpty(div,  textToSearch = u"Telefonas")
        c.fax = getFieldNotEmpty(div,  textToSearch = u"Faksas")
        c.webpage = getFieldNotEmpty(div,  textToSearch = u"Svetainė", doubleNext = True)
        c.email = getFieldNotEmpty(div,  textToSearch = u"El.paštas", doubleNext = True)
        return c
        
    def getContactList(self):
        contactDivs = self.soupForm.findAll("div", "contact")
        for div in contactDivs:
            yield self.extractContact(div)

        

class MunicipalityListReader:

    def __init__(self, url):
        self.soupForm = readUrl(url)
        self.url = url

    def getMunicipalityList(self):
        """ reads web page http://www.lrvalstybe.lt/savivaldybes-4906/   and yields urls to each of the municipality"""
        mapTag = self.soupForm.find("map", id="lietuva_Map")
        if mapTag is None:
            raise LrValstybeCrawlerException(u"Could not find map tag in page %s, maybe web page structure has changed?" % self.url)

        loopTag = mapTag.findNextSibling()
        while loopTag is not None:
            if loopTag.name != "a":
                break
            yield extractTextAndUrl(loopTag)

            loopTag = loopTag.findNextSibling().findNextSibling()

  