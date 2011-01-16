from pjutils.exc import ChainnedException
import re

class StringIsNotAHouseNumberException(ChainnedException):
    pass

def isStringStreetHouseNumber(string):
    """ returns where a string is a valid house number or not. For example,
    4, 3A, 6d, 8 are all valid house numbers,  18aa is not, since it contains double letter"""
    # first element must be digit
    # first before last must be strictly digit
    # last element must be either digit, or letter
    if (string == ""):
        return False
    if (string == None):
        return False

    if string[0].isdigit() == False:
        return False
    if (len(string)) < 2:
        return True

    # check that last element is alphanumeric
    if string[-1].isalnum() == False:
        return False

    # check last element before last must be strictly digit. I.e. we do not allow street addresses to contain
    # two letters, such as "Kings road 5ad"
    if string[-2].isdigit() == False:
        return False;

    return True

def ifHouseNumberContainLetter(fromNumber):
    # maybe it contains letter
    m = re.search('[a-zA-Z]', fromNumber)
    if (m is not None):
        return True
    return False

def removeLetterFromHouseNumber(fromNumber):
    # maybe it contains letter
    m = re.search('[a-zA-Z]', fromNumber)
    if (m is not None):
        group = m.group()
        letterFrom = group
        fromNumber = fromNumber.replace(group, "")
    return fromNumber