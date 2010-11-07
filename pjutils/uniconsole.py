""" Import this package if your host os does not support printing Unicode characters out of the box.
It will replace sys.stdout stream with a stream which automaticall converts to utf-8 before printing
to output"""

import sys, os
platforms = ["linux2", "win32"]

if sys.platform in platforms:
    class UniStream(object):
        __slots__= "fileno", "softspace",
        def __init__(self, fileobject):
            self.fileno= fileobject.fileno()
            self.softspace= False
        def flush(self):
            pass

        def write(self, text):
            if isinstance(text, unicode):
                os.write(self.fileno, text.encode("utf_8"))
            else:
                os.write(self.fileno, text)
    sys.stdout= UniStream(sys.stdout)
    sys.stderr= UniStream(sys.stderr)