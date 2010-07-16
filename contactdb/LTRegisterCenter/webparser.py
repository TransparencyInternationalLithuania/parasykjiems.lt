#!/usr/bin/env python
# -*- coding: utf-8 -*-

from urllib2 import urlopen
from ClientForm import ParseResponse
from BeautifulSoup import BeautifulSoup
import re
from pjutils.exc import ChainnedException
from pjutils.uniconsole import *

class PageParseException(ChainnedException):
    pass

class RegisterCenterPage:
    """ a class describing a RegisterCenter page.
    A parsed page will consist of 3 main parts:
    * a location part, which will describe which geographical part this page is describing
    * a links part - this is the main data that the page holds. This will be either district or street names, etc
    * additional links part - a link to "more results". Some cities are very big, so streets will be displayed on
    several pages. So this will contain links to those other pages."""


    # a list of str objects
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

class RegisterCenterParser:
    def __init__(self, htmlText):
        self.soupForm = BeautifulSoup(htmlText)

    def _removeLineBreaks(self, string):
        rootLocation = re.sub(r'\n', ' ', str(string))
        rootLocation = rootLocation.replace("   ", " ")
        return rootLocation

    def _GetLocationsFirstTag(self):
        # find first location tage
        lt = self.soupForm.find(text=re.compile("LIETUVOS|RESPUBLIKA"))
        if (lt is None):
            print "Could not find 'LIETUVOS RESPUBLIKA' tag, page has been changed. Damn"
            raise PageParseException("Could not find 'Lietuvos Respublika' tag, can not continue")
        return lt

    def GetLocation(self):
        """ extracts from a register page a list of locations.
        A location looks something like this (without all the htmls tags of course)       
LIETUVOS RESPUBLIKA / Tauragės apskr. / Pagėgių sav. / Natkiškių sen. / Natkiškių k.
        """
        location = []
        lt = self._GetLocationsFirstTag()

        # always add first location. also remove any \n characters with regexp

        location.append(self._removeLineBreaks(lt))

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
            location.append(self._removeLineBreaks(nextName))

            # check if this is the last tag by searching for <br> tags
            brTag = root.next.next.next
            if (hasattr(brTag, "name") == False):
                continue
            if (brTag.name.find('br') >= 0):
                break
        return location

    def ExtractLinkCell(self, cellTag):
        cell = LinkCell()
        cell.text = self._removeLineBreaks(cellTag.text)
        if (cellTag.next is not None):
            href = cellTag.next
            if (hasattr(href, "attrs") == True):
                hrefAttr = href.attrs[0]
                cell.href = hrefAttr[1]
        return cell

    def GetLinks(self):
        """ Finds a table containing a list of streets/districts/counties in the page
        and extracts that table to a list"""
        locationFirstTag = self._GetLocationsFirstTag()
        headingCell = locationFirstTag.findNext(text=re.compile("Apskrities|Savivaldybės|Seniūnijos|centras|Pavadinimo|vardininkas|Gatv"))

        if (headingCell is None):
            print self.soupForm.prettify()
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

    def parse(self):
        """ Parses a RegisterCenter page and returns a RegisterCenterPage object
        containing extracted info"""
        page = RegisterCenterPage()

        # extract locations from web page
        page.location = self.GetLocation()

        page.links = self.GetLinks()


        """
        tableRows = h1.next.next.findAll("td")
        values = []
        for row in tableRows:
            if (len(row.contents) > 0):
                values.append(row.contents[0])
            values.append("\t")

        print "".join(values)"""
        return page

