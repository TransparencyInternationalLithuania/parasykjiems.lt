from django.core.management.base import BaseCommand
from contactdb.models import Person, Institution, PersonPosition
from pjutils.timemeasurement import TimeMeasurer
from pjutils.djangocommands import ExecManagementCommand
from django.db import connection, transaction


class Command(BaseCommand):
    args = '<>'
    help = 'Imports initial / automatically unchangeable data. Such data is constituencies and constituency streets for LT data'

    def getDuplicateNames(self, cursor):
        # Data retrieval operation - no commit required
        sql = """ select  name, surname from %s p
group by name, surname
having count(*) > 1
""" % Person.objects.model._meta.db_table
        c = cursor.execute(sql)
        return c.fetchall()

    def getDuplicateDetails(self, cursor, name, surname):
        formatters = {"name":name,
               "surname":surname,
               "personPosition":PersonPosition.objects.model._meta.db_table,
               "person":Person.objects.model._meta.db_table,
               "institution":Institution.objects.model._meta.db_table
               }
        sql = """SELECT p.name, p.surname, p.disambiguation, i.name, i.institutionType_id FROM "%(personPosition)s"  pp
 INNER JOIN "%(person)s" p ON  ("p"."id" = pp."person_id")
 INNER JOIN "%(institution)s" i ON (i."id" = pp."institution_id")
 where p.name like '%(name)s' and p.surname like '%(surname)s'""" % formatters

        c = cursor.execute(sql)
        return c.fetchall()

    def hasMissingDisambiguationColumn(self, duplicateDetails):
        disambiguationColumns = [d[2] for d in duplicateDetails]
        for c in disambiguationColumns:
            if c == u"":
                return True



    def handle(self, *args, **options):
        time = TimeMeasurer()
        cursor = connection.cursor()
        duplicateNames = self.getDuplicateNames(cursor)

        print "name,surname,disambiguation,name,institutionType_id"
        for name, surname in duplicateNames:
            duplicateDetails = self.getDuplicateDetails(cursor, name, surname)
            if not self.hasMissingDisambiguationColumn(duplicateDetails):
                continue
            for d in duplicateDetails:
                d = [u"%s" % d for d in d]
                print u",".join(d)
            print "\n"




        


        print "finished importing ContactDB. Took %s seconds" % time.ElapsedSeconds()
