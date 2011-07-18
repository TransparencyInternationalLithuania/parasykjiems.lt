import traceback
import sys

class ChainedException(Exception):
    """This whole akward construct is solely for supporting nested exceptions.
    Imagine a situation where a file is being read. Then an IO exception is raised.
    However, in the routine that reads the file we catch this exception, and raise
    new ImportFromFile exception. So far python has no support for containing
    stack traces for both of the exceptions. Update - Python 3 has support for this,
    but Django will not move to Py3 soon enough. When this happens,
    mark this class as deprecated

    When exception is not caught, it is printed out
    to console with all stack-traces, no matter how many nested exceptions are.

    P.s. there is one bug still:
       try:
        raise ChainedException("aaaaaaaaaaaaaa")
    except ChainedException as e:
        pass

    raise ChainedException("bbbbbbbbbbbb")

    This print both stack traces, even bbbbbbbbb exception does not contain any inner exceptions
       """

    def __init__(self, message = None, inner = None):
        exc_type, exc_value, exc_traceback = sys.exc_info()
        
        
        self.exc_type = exc_type
        self.exc_value = exc_value
        self.exc_traceback = exc_traceback
        
        self.message = message
        pass

    def __str__(self):

        if self.exc_type is not None:
            print "\n\n inner exception\n \n"
            traceback.print_exception(self.exc_type, self.exc_value, self.exc_traceback, file=sys.stdout)
            print "\nend of inner exception \n"
        return repr(self.message)


class MethodNotImplementedException(ChainedException):
    pass


if (__name__ == "__main__"):

    try:
        raise ChainedException("my message")
    except ChainedException as e:
    
        try:
            raise ChainedException("custom exception 2", e)
        except ChainedException as e2:
            raise ChainedException("custom exception 3", e)
    