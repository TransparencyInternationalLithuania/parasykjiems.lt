import sys

class GlobalSettingsClass():
    # variables for accessing Lithuanian contact db documents on google docs

    def googleDocsUsers(self):
        print "Define GOOGLE_DOCS_USER and GOOGLE_DOCS_PASSWORD which are used to download Lithuanian contact documents from google docs"

    def __repr__(self):
        return "A global settings repository. Provides some nice help information for undefined names"

    def describeA(self):
        print "Wooo hooo"

    def __getattr__(self, name):

        print "\n\n\n"
        # define a dictionary of functions.  emulating switch here
        printMoreInfo = {'GOOGLE_DOCS_USER' : self.googleDocsUsers,
                         'GOOGLE_DOCS_PASSWORD' : self.googleDocsUsers,
                         'abc' : self.describeA}
        if (name in printMoreInfo):
            printMoreInfo[name]()

        print "\n\n\n"

        print "'%s' was not found in GlobalSettings. Perhaps in the settings_local.pu this value is not yet defined" % name
        print "Look in settings_local.py.template how to set up this variable Then open settins_local.py and define that variable"
        print "\n\n\n"
    
        raise Exception("Please define GlobalSettings.%s  setting" % name)
