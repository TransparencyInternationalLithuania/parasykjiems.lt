#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib2 import urlopen
from ClientForm import ParseResponse
from BeautifulSoup import BeautifulSoup
import re
from contactdb.models import HierarchicalGeoData
from pjutils.exc import ChainnedException
from pjutils.uniconsole import *

# forcing BeautifulSoup to allow <b> tag to have nested table and other tags
import contactdb.models

BeautifulSoup.RESET_NESTING_TAGS['b'] = []

class PageParseException(ChainnedException):
    pass


class LTGeoDataHierarchy:
    """ Each country might have a different hierarchy structure.
    Lithuania has a pre-defined one. Note that there are more possible HierarchicalGeoDataType values
    that are used here"""
    Hierarchy = (HierarchicalGeoData.HierarchicalGeoDataType.Country,
                     HierarchicalGeoData.HierarchicalGeoDataType.County,
                     HierarchicalGeoData.HierarchicalGeoDataType.Municipality,
                     HierarchicalGeoData.HierarchicalGeoDataType.CivilParish,
                     HierarchicalGeoData.HierarchicalGeoDataType.City,
                     HierarchicalGeoData.HierarchicalGeoDataType.Street)

class RegisterCenterPage:
    """ a class describing a RegisterCenter page.
    A parsed page will consist of 3 main parts:
    * a location part, which will describe which geographical part this page is describing. A collection of PageLocation
      objects
    * a links part - this is the main data that the page holds. This will be either district or street names, etc
    * additional links part - a link to "more results". Some cities are very big, so streets will be displayed on
    several pages. So this will contain links to those other pages."""


    # a list of PageLocation objects
    location = []
    # a list of LinkCell objects
    links = []

    # a list of str objects. will contain URLs
    otherPages = []

class LinkCell:
    """ Describes a single cell in a table in RegisterCenter page.
    There will be two types of cells. Cell with only text, and cells with text
    and an URL to sub-data.  This sub-data url will have to be parsed as another RegisterCenter page
    in the next import cycle"""
    text = u""
    href = u""

    def __init__(self, text = None, href = None):
        self.text = text
        self.href = href

    def __str__(self):
        return "text: %s  url: %s" % (self.text, self.href)


class PageLocation:
    """ Each RegisterCenterPage is located in some place in hierarchical order. This class describes
    a single location object in that hierarchical order.
    So RegisterCenterPage will contain a list of PageLocation objects in hierarchical order top to bottom,
    where each level will have a name and a type"""

    # A name of the location, such a street name, or city name, or country name
    name = ""
    # a string describing a location type. It will be a string from data structure defined in
    # HierarchicalGeoData.HierarchicalGeoDataType
    type = ""

    def __init__(self, text, type):
        self.text = text
        self.type = type




class RegisterCenterParser:
    def __init__(self, htmlText):
        self.soupForm = BeautifulSoup(htmlText)

    def _removeLineBreaks(self, string):
        strstr = u"%s" % string
        rootLocation = re.sub(r'\n', ' ', strstr)
        # removing unecessary white spaces
        # this is soooo lame that i do it twice here. Anyone knows how to do better? 
        rootLocation = rootLocation.replace("   ", " ")
        rootLocation = rootLocation.replace("  ", " ")
        return rootLocation

    def _GetLocationsFirstTag(self):
        # find first location tage
        lt = self.soupForm.find(text=re.compile("LIETUVOS|RESPUBLIKA"))
        if (lt is None):
            print "Could not find 'LIETUVOS RESPUBLIKA' tag, page has been changed. Damn"
            raise PageParseException("Could not find 'Lietuvos Respublika' tag, can not continue")
        return lt

    def _NormaliseLocationText(self, text):
        text = text.replace(u"apskr.", u"apskritis")
        text = text.replace(u"sav.", u"savivaldybė")
        text = text.replace(u"sen.", u"seniūnija")
        text = text.replace(u"k.", u"kaimas")
        text = text.replace(u"r. ", u"")
        text = text.replace(u"g.", u"gatvė")
        text = text.replace(u"m.", u"miesto")
        return text


    def _GetNewLocationObject(self, text, hierarchicalLocationPosition):
        type = LTGeoDataHierarchy.Hierarchy[hierarchicalLocationPosition]
        text = self._NormaliseLocationText(text)
        return PageLocation(text, type)


    def GetLocation(self):
        """ extracts from a register page a list of locations.
        A location looks something like this (without all the htmls tags of course)       
LIETUVOS RESPUBLIKA / Tauragės apskr. / Pagėgių sav. / Natkiškių sen. / Natkiškių k.
        """
        location = []
        lt = self._GetLocationsFirstTag()

        # this will determine position in code hierarchy
        hierarchicalLocationPosition = 0

        # always add first location. also remove any \n characters with regexp
        location.append(self._GetNewLocationObject(self._removeLineBreaks(lt), hierarchicalLocationPosition))


        # if first location is contained in bold tag, then no other tags will be present
        if (lt.parent.name == 'b'):
            return location

        # otherwise get the encapsulated a tag
        root = lt.parent.parent

        while (True):
            # get the next <a> tag
            root = root.findNext().findNext()

            # add location name
            nextName = root.next.next

            # go down in the hierarchy
            hierarchicalLocationPosition += 1
            # add new location object
            location.append(self._GetNewLocationObject(self._removeLineBreaks(nextName), hierarchicalLocationPosition))

            # check if this is the last tag by searching for <br> tags
            brTag = root.next.next.next
            if (hasattr(brTag, "name") == False):
                continue
            if (brTag.name.find('br') >= 0):
                break
        return location

    def _constructHyperlink(self, href):
        """ When downloading document from online, the urls are relative, not absolute.
        So fix this to be always absolute"""
        if (href.startswith("http") == True):
            return href
        return "%s%s" % ("http://www.registrucentras.lt", href)

    def ExtractLinkCell(self, cellTag):
        cell = LinkCell()
        cell.text = self._removeLineBreaks(cellTag.text)
        cell.text = self._NormaliseLocationText(cell.text)

        if (cellTag.next is not None):
            href = cellTag.next
            if (hasattr(href, "attrs") == True):
                hrefAttr = href.attrs[0]
                cell.href = self._constructHyperlink(hrefAttr[1])
        return cell

    def GetLinks(self):
        """ Finds a table containing a list of streets/districts/counties in the page
        and extracts that table to a list"""
        locationFirstTag = self._GetLocationsFirstTag()
        headingCell = locationFirstTag.findNext(text=re.compile("Apskrities|Savivaldybės|Seniūnijos|centras|Pavadinimo|vardininkas|Gatv"))

        if (headingCell is None):
            #print self.soupForm.prettify()
            raise PageParseException("Could not find table heading cell tag, page has been changed. Damn")

        tableTag = headingCell.parent.parent.parent

        allRows = tableTag.findAll("tr")
        # skip first row, since it is heading
        allRows = allRows[1:]

        links = []

        for row in allRows:
            rowCells = row.findAll("td")
            cell1 = self.ExtractLinkCell(rowCells[0])
            #cell2 = self.ExtractLinkCell(rowCells[1])
            links.append(cell1)

        return links

    def _otherPageResult(self, res):
        """ returns LinkCell object if it is a hyperlink. Returns None otherwise"""
        if res.name == "b":
            return None
        if (res.name != "a"):
            raise PageParseException("found tag '%s'  instead of <a>. This should not have happened" % (res.name))

        # attrs[0] is the first and only attribute. Then we take second argument from the tuple.
        # first will be attribute name, i.e. href, second will be the actual url
        url = self._constructHyperlink(res.attrs[0][1])
        link = LinkCell(text = res.text, href = url)
        return link

        

    def GetOtherPages(self):
        """ Sometimes a city has many streets. Then results are splitted into pages.
        Here we will get links to those other result pages. """
        locationFirstTag = self._GetLocationsFirstTag()
        rez = locationFirstTag.findNext(text=re.compile("Rezultatų|puslapiai"))
        otherLinks = []
        
        if (rez is None):
            # Could not find results section. This is ok, since not all pages will hve that
            return otherLinks

        firstResult = rez.next


        while (True):
            # extract either hyperlink, either get None if it is bold tag
            otherLink = self._otherPageResult(firstResult)
            if (otherLink is not None):
                otherLinks.append(otherLink)

            # when we encounter page break, break loop
            twoforward = firstResult.next.next
            if (hasattr(twoforward, "name")):
                if (twoforward.name == "br"):
                    break
            # sometimes page breaks is a bit further the line. just check again
            # yes, lame. but works, and fixes unit test
            if (hasattr(twoforward.next, "name")):
                if (twoforward.next.name == "br"):
                    break

            # loop to next hyperlink
            firstResult = firstResult.next.next.next
        return otherLinks
            


        

    def parse(self):
        """ Parses a RegisterCenter page and returns a RegisterCenterPage object
        containing extracted info"""
        page = RegisterCenterPage()

        # extract locations from web page
        page.location = self.GetLocation()

        page.links = self.GetLinks()

        page.otherPages = self.GetOtherPages()


        """
        tableRows = h1.next.next.findAll("td")
        values = []
        for row in tableRows:
            if (len(row.contents) > 0):
                values.append(row.contents[0])
            values.append("\t")

        print "".join(values)"""
        return page

