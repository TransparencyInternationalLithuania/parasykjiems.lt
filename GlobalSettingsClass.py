import sys

class GlobalSettingsBase(object):
    def __init__(self):
        # a list of variable names to functions which print a description
        # of what that variable name will be used for
        self.variablesToFunction = {}

    def printHelpForSetting(self, name):
        print "\n\n\n"

        if (name in self.variablesToFunction):
            self.variablesToFunction[name]()


    def __getattr__(self, name):
        # intercept attribute usage. if attribute does not exist (since we are in this method),
        # print a help string describing what that variables is used for

        self.printHelpForSetting(name)

        print "\n\n\n"

        print "'%s' was not found in GlobalSettings. Perhaps in the settings_local.py this value is not yet defined" % name
        print "Look in settings_local.py.template how to set up this variable Then open settings_local.py and define that variable"
        print "\n\n\n"

        raise Exception("Please define %s  setting" % name)

class GlobalSettingsSMTP(GlobalSettingsBase):
    pass

class GlobalSettingsIMAP(GlobalSettingsBase):
    pass

class GlobalSettingsMail(GlobalSettingsBase):

    def _feedbackEmail(self):
        print "Send a feedback email, written by website end user, to this email address. Usually parasykjiems@gmail.com"

    def __init__(self):
        super(GlobalSettingsMail, self).__init__();

        self.mailVariables = {'feedbackEmail': self._feedbackEmail}
        self.variablesToFunction = dict(self.variablesToFunction, **self.mailVariables)


class GlobalSettingsClass(GlobalSettingsBase):
    # a root class from which all environment variables will be taken
    # will print help if given variable will not be defined
    def __init__(self):
        super(GlobalSettingsClass, self).__init__();

        globalSettingsObjectVariables = {'GOOGLE_DOCS_USER' : self.googleDocsUsers,
                         'GOOGLE_DOCS_PASSWORD' : self.googleDocsUsers,
                         'EnableWWWForLTGeoTests' : self._EnableWWWForLTGeoTests,
                         'LTGeoDataParseUrl' : self._LTGeoDataParseUrl,
                         'LANGUAGES' : self.Languages,
                         'PROFANITIES_LIST' : self.Profanities,
                         'MAIL_SERVER' : self.MailServ,
                         'MAIL_SERVER_TYPE' : self.MailServ,
                         'MAIL_USERNAME' : self.MailServ,
                         'MAIL_PASSWORD' : self.MailServ,
                         'MAIL_PORT' : self.MailServ,}

        self.variablesToFunction = dict(self.variablesToFunction, **globalSettingsObjectVariables)

    # variables for accessing Lithuanian contact db documents on google docs
    def googleDocsUsers(self):
        print "Define GOOGLE_DOCS_USER and GOOGLE_DOCS_PASSWORD which are used to download Lithuanian contact documents from google docs"

    def __repr__(self):
        return "A global settings repository. Provides some nice help information for undefined names"

    def _EnableWWWForLTGeoTests(self):
        print "Define EnableWWWForLTGeoTests settings. Needed to check if run geo tests against real world data. Default is False "

    def Languages(self):
        print "Define used Languages. Defaults are Lithuanian and English "

    def Profanities(self):
        print "Define profanities (nasty words) list in local_settings.py "

    def MailServ(self):
        print "Define mail server, and settings where responses are coming from."

    def _LTGeoDataParseUrl(self):
        print """Define an URL for Lithuanian RegisterCenter root page. From that page data will be extracted
        hierarchicaly from top to bottom. Don't set this variable to root url, unless you are on production.
        We dont want to bomb RegisterCetnter.lt with too many uneccesary requests"""
