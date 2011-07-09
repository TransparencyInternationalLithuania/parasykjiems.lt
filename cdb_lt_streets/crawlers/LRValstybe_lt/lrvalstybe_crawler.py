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
    text = text.replace(u"»", u"").strip()
    url = ahrefTag.attrs[0][1]
    if url is not None and url != u"":
        url = u"%s%s" % ("http://www.lrvalstybe.lt", url)
    return text, url

def findAhrefTag(soupForm, linkText):
    link = soupForm.find(text=re.compile(linkText))
    if link is None:
        return None
    if link.parent.name != u"a":
        return None
    return link.parent

class MunicipalityPageReader:

    def __init__(self, municipalityUrl):
        self.url = municipalityUrl
        self.soupForm = readUrl(municipalityUrl)
        pass


    def getCivilParishListUrl(self):
        # usually there will be a link to list of seniūnaitijos
        HRefTag = findAhrefTag(self.soupForm, u"Seniūnijos")
        if HRefTag is not None:
            return extractTextAndUrl(HRefTag)
        return None, None




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
        # sometimes next element will be equal to next sibling, in case where div does not contain any text inside
        # in this case return text element, which will be usually empty.
        # otherwise we would get a next html element, which is not what we want
        if d.next == d.nextSibling:
            v = d.text
        else:
            v = d.next
    else:
        v = d.next.next

    if hasattr(v, "replace") and v.strip is not None:
        v = v.replace(u"\n", u"")
        v = v.replace(u"\r", u"")

    return v


class MunicipalityContactReader:
    def __init__(self, url):
        self.soupForm = readUrl(url)
        self.url = url

    def extractContact(self, div):
        c = Contact()
        c.name = getFieldNotEmpty(div, elementType="div", cssClass="con_name", doubleNext = True)
        c.title = getFieldNotEmpty(div, elementType="div", cssClass="con_title", doubleNext = False)
        # sometimes there might be a bad html formed.  For example,
        # this page has 4 contact divs, not 3 (check with FireBug)
        # http://www.lrvalstybe.lt/pabirzes-seniunija-5157/
        if c.title is None:
            return None
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
            res = self.extractContact(div)
            if res is None:
                continue
            yield res

        

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


class CivilParishListReader:

    def __init__(self, municipalityUrl, civilParishUrl):
        self.municipalityUrl = municipalityUrl
        self.civilParishUrl = civilParishUrl

    def getSingleCivilParish(self):
        soupForm = readUrl(self.municipalityUrl)
        HRefTag = findAhrefTag(soupForm, u"seniūnija")
        if HRefTag is None:
            return None, None
        return extractTextAndUrl(HRefTag)

    def getCivilParishList(self):
        """ reads web pages such as http://www.lrvalstybe.lt/seniunijos-6499/   and yields urls to each of the civil parish"""
        if self.civilParishUrl is None:
            yield self.getSingleCivilParish()
            return

        soupForm = readUrl(self.civilParishUrl)

        naujienos = soupForm.find("div", "middle_naujienos")
        firstUrl = naujienos.next.next.next.next
        secondUrl = firstUrl.nextSibling.nextSibling
        thirdUrl = secondUrl.nextSibling.nextSibling

        firstParish = thirdUrl.nextSibling.nextSibling.nextSibling.nextSibling
        
        while firstParish is not None:
            if firstParish.name != "a":
                break
            yield extractTextAndUrl(firstParish)

            firstParish = firstParish.findNextSibling().findNextSibling()

  