from urllib2 import urlopen
from ClientForm import ParseResponse
from BeautifulSoup import BeautifulSoup
import re

class RegisterCenterPage:
    location = []

class RegisterCenterParser:
    def __init__(self, htmlText):
        self.htmlText = htmlText

    def _removeLineBreaks(slef, string):
        rootLocation = re.sub(r'\n', ' ', str(string))
        rootLocation = rootLocation.replace("   ", " ")
        return rootLocation

    def GetLocation(self, lt):
        location = []

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

    def parse(self):
        soupForm = BeautifulSoup(self.htmlText)


        lt = soupForm.find(text=re.compile("LIETUVOS|RESPUBLIKA"))

        if (lt is None):
            print "Could not find 'LIETUVOS RESPUBLIKA' tag, page has been changed. Damn"
            return
        page = RegisterCenterPage()
        page.location = self.GetLocation(lt)




        """
        tableRows = h1.next.next.findAll("td")
        values = []
        for row in tableRows:
            if (len(row.contents) > 0):
                values.append(row.contents[0])
            values.append("\t")

        print "".join(values)"""
        return page

