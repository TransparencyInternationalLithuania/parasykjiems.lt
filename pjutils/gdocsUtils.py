import logging
import os
from pjutils.exc import ChainnedException
import csv
from settings import GlobalSettings

try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import gdata.spreadsheet.service
import gdata.service
import gdata.spreadsheet
logger = logging.getLogger(__name__)
import gdata.docs.data
import gdata.docs.client
import gdata.spreadsheet.service
from distutils import dir_util

class GoogleDocsError(ChainnedException):
    pass

class GoogleDocDownloader:
    """ Downloads a google doc, and saves it to a file as csv file.
    This class is using an old way to connect to google docs and download a doc. This takes much longer,
    but we can control the way the file is saved to disk.

    You can use some of the helper methods defined in the same package instead of using this class directly"""

    def __init__(self, delimiter = ","):
        self.client = SpreadSheetClient(GlobalSettings.GOOGLE_DOCS_USER, GlobalSettings.GOOGLE_DOCS_PASSWORD)

    def _openWriter(self, fileName, row, defaultColumnOrder = None):
        """ creates a new DictWriter object from row object. Writes header row"""

        if defaultColumnOrder is None:
            fieldNames = [k for k in row.iterkeys()]
        else:
            fieldNames = defaultColumnOrder
            existing = {}
            for f in fieldNames:
                existing[f] = ""
            for k in row.iterkeys():
                if existing.has_key(k) == False:
                    fieldNames.append(k)
                    existing[k] = ""


        writer = csv.DictWriter(open(fileName, "wb"), fieldNames)

        headers = dict( (n,n) for n in fieldNames )
        writer.writerow(headers)

        return writer

    def downloadDoc(self, docName, fileName, defaultColumnOrder = None):
        print "downloading  '%s' to '%s'" % (docName, fileName)
        docName = docName.encode("utf-8")
        self.client.SelectSpreadsheet(docName)
        self.client.SelectWorksheet(0)


        #writer = csv.writer(open(output, "wb"), csv.excel_tab)
        fileName = os.path.join(os.getcwd(), fileName)

        writer = None
        for row in self.client.GetAllRows():
            # row is a custom object, so lets construct a normal dictionary from it with keys and values
            val = self.client.ToDictionaryFromRow(row)
            if (writer is None):
                writer = self._openWriter(fileName, val, defaultColumnOrder = defaultColumnOrder)
            writer.writerow(val)
        print "ok"

        self.client.GetAllRows()


def downloadDoc(login, docName, fileName, defaultColumnOrder = None):
    """ Creates a path if it does not exist, and uses GoogleDocDownloader to download doc to disk and
     saves it as csv file"""
    dir_util.mkpath(os.path.dirname(fileName))
    GoogleDocDownloader().downloadDoc(docName, fileName, defaultColumnOrder = defaultColumnOrder)


class GoogleDocsLogin():
    def __init__(self, username, passw):
        self.username = username
        self.passw = passw
        self.spreadsheets_client = None

        logger.info("Logging into google docs")
        self.client = gdata.docs.client.DocsClient(source='ManoValstybe-Para6ykjiems-v.0.0.1')
        self.client.ssl = True  # Force all API requests through HTTPS
        self.client.http_client.debug = True  # Set to True for debugging HTTP requests
        self.client.ClientLogin(username, passw, self.client.source)
        logger.info("Logged in into google docs")

    def UseSpreadSheetToken(self):
        if (self.spreadsheets_client is None):
            self.spreadsheets_client = gdata.spreadsheet.service.SpreadsheetsService(source='ManoValstybe-Para6ykjiems-v.0.0.1')
            self.spreadsheets_client.ClientLogin(self.username, self.passw, self.client.source)

        # substitute the spreadsheets token into our client
        self.docs_token = self.client.auth_token
        self.client.auth_token = gdata.gauth.ClientLoginToken(self.spreadsheets_client.GetClientLoginToken())


    def UseDocsToken(self):
        self.client.auth_token = self.docs_token  # reset the DocList auth token

class GoogleDocNotFound(ChainnedException):
    pass


class GoogleDocsUploader():
    def __init__(self, gdocsLogin, documentTitle):
        self.gdocsLogin = gdocsLogin
        self.entry = None
        uri = u'/feeds/default/private/full?title=%s&title-exact=true&max-results=5' % documentTitle
        uri = uri.encode('utf-8')
        feed = self.gdocsLogin.client.GetDocList(uri=uri)
        try:
            self.entry = feed.entry[0]
        except IndexError:
            raise GoogleDocNotFound("Google document with title '%s' was not found. Double check that such document realy exist. Maybe you forgot to create it?" % documentTitle )

        msg = u"Selected document '%s'" %  self.entry.title.text
        logger.info(msg)

    def replaceContents(self, fileName):
        ms = gdata.data.MediaSource(file_path=fileName, content_type='text/csv')
        #self.entry.title.text = 'updated document'

        try:
            self.gdocsLogin.client.Update(self.entry, media_source=ms)
        except gdata.client.RequestError as e:
            raise GoogleDocsError(message="Could not upload document '%s', error" % fileName, inner = e)

        msg = u"Document '%s' contents changed" % (self.entry.title.text)
        logger.info(msg)


    def downloadDocument(self, fileName):
        """ this function downloads a file as csv file.
        However, if the cells have new line symols, the csv file will not handle them correctly, i.e. there
        will be line breaks in the csv file

        Use GoogleDocDownloader instead to downloadDocs.
        """

        logger.info('Downloading spreadsheet to %s...' % fileName)
        dir_util.mkpath(os.path.dirname(fileName))
        contents = self.gdocsLogin.client.GetFileContent(self.entry.GetAlternateLink().href)
        for c in contents:
            print c

        self.gdocsLogin.UseSpreadSheetToken()
        self.gdocsLogin.client.Export(self.entry, fileName, gid=0)
        self.gdocsLogin.UseDocsToken()
        logger.info('ok')




class SpreadSheetClient:
    """ A class to connect to Google docs and download spreadsheet document
    To download a doc you first need to know an email and password for that email.

    This is an old method to connect to google docs,  GoogleDocsLogin and GoogleDocsUploader use the new
     way to connect and work with data, but it did not work good enough for all cases

    method GetAllRows can be used to download document and then manually save all the data to file
    """

    def __init__(self, email, password):
        self.gd_client = gdata.spreadsheet.service.SpreadsheetsService()
        self.gd_client.email = email
        self.gd_client.password = password
        self.gd_client.source = 'parasykJiems.lt'
        self.gd_client.ProgrammaticLogin()
        self.curr_key = ''
        self.curr_wksht_id = ''

    def _PrintFeed(self, feed):
        """ A helper method to print contents of a feed"""
        for i, entry in enumerate(feed.entry):
          if isinstance(feed, gdata.spreadsheet.SpreadsheetsCellsFeed):
            print '%s %s\n' % (entry.title.text, entry.content.text)
          elif isinstance(feed, gdata.spreadsheet.SpreadsheetsListFeed):
            print '%s %s %s' % (i, entry.title.text, entry.content.text)
            # Print this row's value for each column (the custom dictionary is
            # built using the gsx: elements in the entry.)
            print 'Contents:'
            for key in entry.custom:
              print '  %s: %s' % (key, entry.custom[key].text)
            print '\n',
          else:
            print '%s %s\n' % (i, entry.title.text)

    def SelectSpreadsheet(self, name):
        """ selects a spreadsheet given a spreadsheet name.
        Case insesitive"""
        feed = self.gd_client.GetSpreadsheetsFeed()
        feedDict = dict([(f.title.text, f) for position, f in enumerate(feed.entry)])
        feedEntry = feedDict[name]
        id_parts = feedEntry.id.text.split('/')
        self.curr_key = id_parts[len(id_parts) - 1]

    def SelectWorksheet(self, worksheetNumber):
        """ Selects a worksheet using worksheet number. Zero based"""
        feed = self.gd_client.GetWorksheetsFeed(self.curr_key)
        id_parts = feed.entry[worksheetNumber].id.text.split('/')
        self.curr_wksht_id = id_parts[len(id_parts) - 1]
        self._CreateListFeed()

    def DeleteAllRows(self):
        count = 0
        for i, entry in enumerate(self.listFeed.entry):
            count += 1
        logger.info("will delete %s rows" % count)
        for i in range(0, count):
            self.gd_client.DeleteRow(listFeed.entry[i])
            logger.debug("deletig %s / %s" % (i, count))
        logger.info("deleted")

    def GetRowsCount(self):
        count = 0
        for i, entry in enumerate(self.listFeed.entry):
            count += 1
        return count


    def ToDictionaryFromRow(self, googleRow):
        """ builds a dictionary, and encodes values with utf-8 from a google row.
        See GetAllRows() for details. You can feed results from GetAllRows
        directly to this function"""
        d = dict([(k, v.text) for k, v in googleRow.iteritems()])

        for k in d.iterkeys():
            if d[k] is None:
                continue
            d[k] = d[k].replace("\n", " ")

            d[k] = d[k].encode("utf-8")
        return d

    def GetListFeed(self):
        return self.listFeed

    def _CreateListFeed(self):
        self.listFeed = self.gd_client.GetListFeed(self.curr_key, self.curr_wksht_id)
        return self.listFeed


    def GetAllRows(self):
        """ returns a a generator which yields a dictionary of values for each row"""
        for i, entry in enumerate(self.listFeed.entry):
            yield entry.custom