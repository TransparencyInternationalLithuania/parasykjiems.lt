import os
import csv
from progressbar import ProgressBar, Bar, ETA
from django.db.models import Q


def export_models(query, filename, fields):
    """Exports model objects to csv file.

    'fields' should be a list of strings, specifying which fields of
    the objects to export.
    """
    destdir = os.path.dirname(filename)
    if not os.path.exists(destdir):
        os.makedirs(destdir)

    print 'Exporting to "{}".'.format(filename)
    with open(filename, 'wb') as f:
        w = csv.DictWriter(f, fields)
        w.writeheader()
        for obj in ProgressBar([ETA(), ' ', Bar()])(query):
            row = {}
            for field in fields:
                row[field] = unicode(obj.__dict__[field]).encode('utf-8')
            w.writerow(row)


def import_models(filename, model, key, fields, additional_filter=None):
    """Imports models from CSV file 'filename'.

    The CSV file should contain a header, and include all 'fields' and
    also the 'key' field as columns.

    'additional_filter' may be a dictionary, used to restrict
    filtering, when checking if a model already exists.
    """
    def d(s):
        if s:
            return s.decode('utf-8').strip()
        else:
            return u''

    def countlines(filename):
        with open(filename) as f:
            for i, l in enumerate(f):
                pass
            return i + 1

    def progressreader(filename):
        print 'Importing from "{}":'.format(filename)
        count = countlines(filename)
        f = open(filename, 'rb')
        reader = csv.DictReader(f)
        widgets = [ETA(), ' ', Bar()]
        return ProgressBar(widgets=widgets, maxval=count)(reader)

    new_objects = 0
    for row in progressreader(filename):
        filterdict = {key: d(row[key])}
        if additional_filter:
            filterdict.update(additional_filter)

        obj, created = model.objects.get_or_create(**filterdict)
        if created:
            new_objects += 1
        for field in fields:
            obj.__dict__[field] = d(row[field])
        obj.save()
    print "Created {} new objects.".format(new_objects)
