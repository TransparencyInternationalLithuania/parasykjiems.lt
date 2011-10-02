from django.db import models


_NAME_LEN = 200


class RepresentativeChange(models.Model):
    # These fields are used for lookup.
    institution = models.CharField(max_length=_NAME_LEN)
    kind_name = models.CharField(max_length=_NAME_LEN)

    # If this field is true, the change represents a deletion istead
    # of an update.
    delete = models.BooleanField(default=False)

    # These fields may be None if they should be left unchanged on update.
    name = models.CharField(max_length=_NAME_LEN, null=True, default=None)
    email = models.CharField(max_length=_NAME_LEN, null=True, default=None)
    phone = models.CharField(max_length=_NAME_LEN, null=True, default=None)
    address = models.CharField(max_length=_NAME_LEN, null=True, default=None)
    other_info = models.CharField(max_length=_NAME_LEN,
                                  null=True,
                                  default=None)

    def __unicode__(self):
        return u'{} [{}, {}] {!r}, {!r}, {!r}, {!r}, {!r}'.format(
            '-' if self.delete else '+',
            self.institution, self.kind_name,
            self.name, self.email, self.phone, self.address, self.other_info)
