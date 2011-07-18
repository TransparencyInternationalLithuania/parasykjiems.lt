import warnings


def deprecated(message = None):
    def issueDeprecated(func):
        """This is a decorator which can be used to mark functions
        as deprecated. It will result in a warning being emmitted
        when the function is used.

        .Net and others have Obsolete or similar concept. I am not
        familiar with such concept in Python. If Py has support for it,
        use the Python suggested way instead, and remove this
        method"""
        def newFunc(*args, **kwargs):
            warnings.warn("Call to deprecated function %s. \n %s" % (func.__name__, message),
                          category = DeprecationWarning)
            return func(*args, **kwargs)
        newFunc.__name__ = func.__name__
        newFunc.__doc__ = func.__doc__
        newFunc.__dict__.update(func.__dict__)
        return newFunc
    return issueDeprecated
