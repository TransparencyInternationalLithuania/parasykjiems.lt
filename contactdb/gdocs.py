import logging

try:
  from xml.etree import ElementTree
except ImportError:
  from elementtree import ElementTree
import gdata.spreadsheet.service
import gdata.service
import atom.service
import gdata.spreadsheet
import atom
import getopt
import sys
import string
logger = logging.getLogger(__name__)


class SpreadSheetUpdater:
    def __init__(self, spreadSheetClient):
        self.spreadSheetClient = spreadSheetClient
        self.gd_client = self.spreadSheetClient.gd_client
        self.feed = self.spreadSheetClient.GetListFeed()

    def AppendRow(self, row_data):
        entry = self.gd_client.InsertRow(row_data, self.spreadSheetClient.curr_key, self.spreadSheetClient.curr_wksht_id)
        if isinstance(entry, gdata.spreadsheet.SpreadsheetsList) == False:
            logger.error('Insert failed')

    def UpdateRow(self, i, row_data):
        entry = self.gd_client.UpdateRow(self.feed.entry[i], row_data)
        if isinstance(entry, gdata.spreadsheet.SpreadsheetsList) == False:
            logger.error('Update failed')

    def DeleteRow(self, i):
        self.gd_client.DeleteRow(self.feed.entry[i])


class SpreadSheetClient:
    """ A class to connect to Google docs and download spreadsheet document
    To download a doc you first need to know an email and password for that email.
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