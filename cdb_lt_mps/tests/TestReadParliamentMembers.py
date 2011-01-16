from django.test.testcases import TestCase
from cdb_lt_mps.management.commands.importMPs import LithuanianMPsReader

scriptPath = os.path.dirname( os.path.realpath( __file__ ) )

class TestReadParliamentMembers(TestCase):
    allRecords = scriptPath + "/parliament members.txt"

    def countNumberOfRecords(self, fileName):
        reader = LithuanianMPsReader(fileName)
        count = 0
        for l in reader.ReadParliamentMembers():
            count += 1
        return count

    def test_AllRecors_count(self):
        self.assertEqual(self.countNumberOfRecords(self.allRecords), 71)

    def test_Read_first_record(self):

        reader = LithuanianMPsReader(self.allRecords)
        for loc in reader.ReadParliamentMembers():
            self.assertEqual(loc.constituency.nr, 1)
            self.assertEqual(loc.constituency.name, u"Naujamiesčio")
            self.assertEqual(loc.name, "Irena")
            self.assertEqual(loc.surname, u"Degutienė")
            self.assertEqual(loc.email, "Irena.Degutiene@lrs.lt")
            break;