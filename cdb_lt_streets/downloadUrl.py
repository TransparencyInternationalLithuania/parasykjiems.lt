from urllib2 import urlopen
import sys

if __name__ == "__main__":

    url = sys.argv[1]
    print "url : %s" % (url)
    response = urlopen(url)
    lines = "".join(response.readlines())
    for l in lines:
        print l