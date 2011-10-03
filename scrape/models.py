from django.db import models
from search.models import Representative, Institution, RepresentativeKind


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
    other_info = models.CharField(max_length=_NAME_LEN,
                                  null=True,
                                  default=None)

    def __init__(self, *args, **kwargs):
        super(RepresentativeChange, self).__init__(*args, **kwargs)
        maybe_rep = Representative.objects.filter(
            institution=Institution.objects.get(name=self.institution),
            kind=RepresentativeKind.objects.get(name=self.kind_name))
        if maybe_rep.exists():
            self.rep = maybe_rep[0]
        else:
            self.rep = None

    def name_changed(self):
        return (self.delete or
                (not self.rep) or
                (self.name and (self.rep.name != self.name)))

    def phone_changed(self):
        return (self.delete or
                (not self.rep) or
                (self.phone and (self.rep.phone != self.phone)))

    def email_changed(self):
        return (self.delete or
                (not self.rep) or
                (self.email and (self.rep.email != self.email)))

    def other_info_changed(self):
        return (self.delete or
                (not self.rep) or
                (self.other_info and (self.rep.other_info != self.other_info)))

    def __unicode__(self):
        return (u'{0} [{1.institution}, {1.kind_name}] '
                u'{1.name!r}, {1.email!r}, {1.phone!r}, {1.other_info!r}'
                .format('-' if self.delete else '+',
                        self))
