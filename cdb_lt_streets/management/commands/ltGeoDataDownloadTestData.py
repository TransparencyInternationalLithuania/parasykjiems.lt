from django.core.management.base import BaseCommand
from django.core import management
from cdb_lt_streets.tests.TestLTRegisterCenter import LTRegisterCenterHtmlData
from urllib2 import urlopen


class Command(BaseCommand):
    args = '<>'
    help = """Prints contents of queue"""


    def handle(self, *args, **options):

        for pack in LTRegisterCenterHtmlData.allSources:
            if (len(pack) < 2):
                continue
            fileName, url = pack
            #url = sys.argv[1]
            print "url : %s" % (url)
            response = urlopen(url)
            lines = "".join(response.readlines())
            #print lines
            print "writing file %s" % (fileName)
            f = open(fileName, mode="w")
            f.writelines(lines)
            f.close()

