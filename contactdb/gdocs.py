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




class SpreadSheetClient:
    def __init__(self, email, password):
        self.gd_client = gdata.spreadsheet.service.SpreadsheetsService()
        self.gd_client.email = email
        self.gd_client.password = password
        self.gd_client.source = 'parasykJiems.lt'
        self.gd_client.ProgrammaticLogin()
        self.curr_key = ''
        self.curr_wksht_id = ''
        self.list_feed = None

    def _PrintFeed(self, feed):
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
        Ignores case"""
        feed = self.gd_client.GetSpreadsheetsFeed()
        feedDict = dict([(f.title.text, f) for position, f in enumerate(feed.entry)])
        feedEntry = feedDict[name]
        id_parts = feedEntry.id.text.split('/')
        self.curr_key = id_parts[len(id_parts) - 1]

    def SelectWorksheet(self, worksheetNumber):
        feed = self.gd_client.GetWorksheetsFeed(self.curr_key)
        id_parts = feed.entry[worksheetNumber].id.text.split('/')
        self.curr_wksht_id = id_parts[len(id_parts) - 1]

    def GetAllRows(self):
        """ returns a a generator which yields a dictionary of values for each row"""
        listFeed = self.gd_client.GetListFeed(self.curr_key, self.curr_wksht_id)
        for i, entry in enumerate(listFeed.entry):
            yield entry.custom
        

    def _PromptForSpreadsheet(self):
        # Get the list of spreadsheets
        feed = self.gd_client.GetSpreadsheetsFeed()
        self._PrintFeed(feed)
        input = raw_input('\nSelection: ')
        id_parts = feed.entry[string.atoi(input)].id.text.split('/')
        self.curr_key = id_parts[len(id_parts) - 1]

    def _PromptForWorksheet(self):
        # Get the list of worksheets
        feed = self.gd_client.GetWorksheetsFeed(self.curr_key)
        self._PrintFeed(feed)
        input = raw_input('\nSelection: ')
        id_parts = feed.entry[string.atoi(input)].id.text.split('/')
        self.curr_wksht_id = id_parts[len(id_parts) - 1]

    def _ListGetAction(self):
        # Get the list feed
        self.list_feed = self.gd_client.GetListFeed(self.curr_key, self.curr_wksht_id)
        self._PrintFeed(self.list_feed)


a =  SpreadSheetClient("parasykjiems@gmail.com", "i#R?M.Xfi`>f:LMa")