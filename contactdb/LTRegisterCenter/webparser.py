from urllib2 import urlopen
from ClientForm import ParseResponse
from BeautifulSoup import BeautifulSoup

class RegisterCenterPage:
    location = []

class RegisterCenterParser:
    def __init__(self, htmlText):
        self.htmlText = htmlText

    def GetLocation(self, lt):
        location = []
        location.append(lt)
        if (lt.parent.name == 'b'):
            return location

        root = lt.parent.parent
        while (True):
            root = root.findNext().findNext()
            nextName = root.next.next
            location.append(nextName)

            brTag = root.next.next.next
            if (hasattr(brTag, "name") == False):
                continue
            if (brTag.name.find('br') >= 0):
                break
        return location

    def parse(self):
        soupForm = BeautifulSoup(self.htmlText)


        lt = soupForm.find(text="LIETUVOS RESPUBLIKA")

        if (lt is None):
            print "Could not find 'Lietuvos Respublika' tag, page has been changed. Damn"
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

