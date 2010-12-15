######################################################################
##
## DEMO
##
######################################################################
from FeatureBroker import *
import os

# ---------------------------------------------------------------------------------
# Some python module defines a Bar component and states the dependencies
# We will assume that
# - Console denotes an object with a method WriteLine(string)
# - AppTitle denotes a string that represents the current application name
# - CurrentUser denotes a string that represents the current user name
#

class Bar(Component):
   con   = RequiredFeature('Console', HasMethods('WriteLine'))
   title = RequiredFeature('AppTitle', IsInstanceOf(str))
   user  = RequiredFeature('CurrentUser', IsInstanceOf(str))
   def __init__(self):
      self.X = 0
   def PrintYourself(self):
      self.con.WriteLine('-- Bar instance --')
      self.con.WriteLine('Title: %s' % self.title)
      self.con.WriteLine('User: %s' % self.user)
      self.con.WriteLine('X: %d' % self.X)

# ---------------------------------------------------------------------------------
# Some other python module defines a basic Console component
#

class SimpleConsole(Component):
   def WriteLine(self, s):
      print s

# ---------------------------------------------------------------------------------
# Yet another python module defines a better Console component
#

class BetterConsole(Component):
   def __init__(self, prefix=''):
      self.prefix = prefix
   def WriteLine(self, s):
      lines = s.split('\n')
      for line in lines:
         if line:
            print self.prefix, line
         else:
            print

# ---------------------------------------------------------------------------------
# Some third python module knows how to discover the current user's name
#

def GetCurrentUser():
   return os.getenv('USERNAME') or 'Some User' # USERNAME is platform-specific

# ---------------------------------------------------------------------------------
# Finally, the main python script specifies the application name,
# decides which components/values to use for what feature,
# and creates an instance of Bar to work with
#
if __name__ == '__main__':
   print '\n*** IoC Demo ***'
   features.Provide('AppTitle', 'Inversion of Control ...\n\n... The Python Way')
   features.Provide('CurrentUser', GetCurrentUser)
   features.Provide('Console', BetterConsole, prefix='-->') # <-- transient lifestyle
   ##features.Provide('Console', BetterConsole(prefix='-->')) # <-- singleton lifestyle

   bar = Bar()
   bar.PrintYourself()