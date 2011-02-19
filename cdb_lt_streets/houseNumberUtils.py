import logging
from pjutils.exc import ChainnedException
import re
import types
logger = logging.getLogger(__name__)

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

def ContainsNumbers(fromNumber):
    """ returns True if string contains at least one number"""
    if (fromNumber is None):
        return False
    m = re.search('[0-9]', fromNumber)
    if (m is not None):
        return True
    return False

def ContainsHouseNumbers(fromNumber):
    """ returns True if string contains at least one number, and that number is not in the middle of the word.
    For comparison, ContainsNumbers method will return True when a number is found anywhere.
    This will return True only if number is not followed by more than two letters, ore by hyphens, commas, etc"""
    if fromNumber is None:
        return False

    # this regex is not valid, so just do some stupid if checks

    m = re.findall('[0-9]+', fromNumber)
    if m is None:
        return False
    for number in m:
        index = fromNumber.find(number) + len(number)
        if (index < len(fromNumber)):
            ch = fromNumber[index]
            if (ch == u'-'):
                continue
        return True
    return False

def ifHouseNumberContainLetter(fromNumber):
    # pass a string which is likely to be a house number.
    # However, some house numbers contains a letter in the end
    # so this just performs a basic search and will return True if it will
    # find ANY letter (even in beginning of string)
    if type(fromNumber) == types.IntType:
        return False
    m = re.search('[a-zA-Z]', fromNumber)
    if m is not None:
        return True
    return False

def isHouseNumberOdd(fromNumber):
    # convert to string
    if fromNumber is None:
        return None
    number = removeLetterFromHouseNumber(fromNumber)
    number = u"%s" % number
    if number == u"":
        return None

    # check if we contain letter
    number = int(number)
    return number % 2 == 1

def convertNumberToString(number):
    if type(number) == types.IntType:
        number = u"%s" % number
    return number


def depadHouseNumberWithZeroes(number):
    number = convertNumberToString(number)
    number = number.lstrip(u"0")
    if number == u"":
        return u""
    if number[-1] == u"0":
        number = number [:-1]
    return number


def padHouseNumberWithZeroes(number):
    number = convertNumberToString(number)
    if number == u"":
        return number
    letter = u"0"
    if ifHouseNumberContainLetter(number):
        letter = number[-1]
    number = removeLetterFromHouseNumber(number)
    stringLen = len(number)
    pad = 4 - stringLen
    padz = u"".join("0" for i in range(0, pad))

    return "%s%s%s" % (padz, number, letter)

def removeLetterFromHouseNumber(fromNumber):
    if fromNumber is None:
        return fromNumber
    # maybe it contains letter
    if type(fromNumber) == types.IntType:
        return fromNumber
    try:
        m = re.search('[a-zA-Z]', fromNumber)
    except TypeError as e:
        logger.info("type was %s" % type(fromNumber))
        raise e

    if m is not None:
        group = m.group()
        letterFrom = group
        fromNumber = fromNumber.replace(group, "")
    return fromNumber