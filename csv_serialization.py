import os
import csv
from progressbar import ProgressBar, Bar, ETA


def export_models(filename, query, fields):
    """Exports model objects to csv file.

    'fields' should be a list of strings, specifying which fields of
    the objects to export.
    """
    def deep_getattr(obj, field):
        path = field.split('__')
        while len(path) > 0:
            obj = getattr(obj, path.pop(0))
        return obj

    destdir = os.path.dirname(filename)
    if not os.path.exists(destdir):
        os.makedirs(destdir)

    fieldnames = [f[0] if isinstance(f, tuple) else f
                  for f in fields]

    print 'Exporting to "{}".'.format(filename)
    exported = 0
    with open(filename, 'wb') as f:
        w = csv.DictWriter(f, fieldnames)
        w.writeheader()
        for obj in ProgressBar(widgets=[ETA(), ' ', Bar()])(query):
            row = {}
            for field in fields:
                if isinstance(field, tuple):
                    header, field = field
                else:
                    header = field
                row[header] = unicode(deep_getattr(obj, field)).encode('utf-8')
            w.writerow(row)
            exported += 1
    print 'Exported {} objects.'.format(exported)


def import_models(filename, model, keys, fields, additional_filter=None):
    """Imports models from CSV file 'filename'.

    The CSV file should contain a header, and include all 'keys' and
    'fields'.

    'keys' should be a dictionary of header names in CSV to fields in
    the model. The field name may be in the form field1__field2,
    which, like in Django queries, is interpreted as a the field2
    subfield of the model at field1. The model in field1 must exist.

    'fields' is a list of additional fields to set in models in
    accordance to the CSV.

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
    modified_objects = 0
    for row in progressreader(filename):
        filterdict = {}
        for key in keys:
            if isinstance(key, tuple):
                header, field = key
            else:
                header, field = key, key
            filterdict[field] = d(row[header])
        if additional_filter:
            filterdict.update(additional_filter)

        obj, created = model.objects.get_or_create(**filterdict)
        if created:
            new_objects += 1
            for key in keys:
                if isinstance(key, tuple):
                    header, field = key
                    if '__' in field:
                        o, f = field.split('__')
                        omodel = getattr(type(obj), o).field.rel.to
                        setattr(obj, o,
                                omodel.objects.get(
                                    **{f: d(row[header])}))
        else:
            modified_objects += 1
        for field in fields:
            if isinstance(field, tuple):
                header, field = field
            else:
                header = field
            setattr(obj, field, d(row[header]))
        obj.save()
    print "Created {} and modified {} objects.".format(
        new_objects, modified_objects)
