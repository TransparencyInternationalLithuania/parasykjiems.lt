from django.db import models
from search.models import Representative, Institution, RepresentativeKind
from search.search_indexes import RepresentativeIndex
import slug


_NAME_LEN = 200


class RepresentativeChange(models.Model):
    # These fields are used for lookup.
    institution = models.CharField(max_length=_NAME_LEN)
    kind_name = models.CharField(max_length=_NAME_LEN)

    # If this field is true, the change represents a deletion istead
    # of an update.
    delete_rep = models.BooleanField(default=False)

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
        return ((self.rep and self.delete_rep) or
                (not self.rep and not self.delete_rep) or
                ((self.name is not None) and (self.rep.name != self.name)))

    def phone_changed(self):
        return ((self.rep and self.delete_rep) or
                (not self.rep and not self.delete_rep) or
                ((self.phone is not None) and (self.rep.phone != self.phone)))

    def email_changed(self):
        return ((self.rep and self.delete_rep) or
                (not self.rep and not self.delete_rep) or
                ((self.email is not None) and (self.rep.email != self.email)))

    def other_info_changed(self):
        return ((self.rep and self.delete_rep) or
                (not self.rep and not self.delete_rep) or
                ((self.other_info is not None) and
                 (self.rep.other_info != self.other_info)))

    def changed(self):
        return (self.name_changed() or self.phone_changed() or
                self.email_changed() or self.other_info_changed())

    def apply_change(self):
        index = RepresentativeIndex(Representative)
        if self.delete_rep:
            index.remove_object(self.rep)
            self.rep.delete()
        else:
            if self.rep:
                rep = self.rep
                index.remove_object(rep)
            else:
                rep = Representative(
                    institution=Institution.objects.get(name=self.institution),
                    kind=RepresentativeKind.objects.get(name=self.kind_name))

            if self.name is not None:
                rep.name = self.name
            if self.phone is not None:
                rep.phone = self.phone
            if self.email is not None:
                rep.email = self.email
            if self.other_info is not None:
                rep.other_info = self.other_info

            slug.generate_slug(rep,
                               Representative.objects.all(),
                               lambda r: [r.name,
                                          r.kind.name,
                                          r.institution.name])
            rep.save()
            index.update_object(rep)
        self.delete()

    def __unicode__(self):
        return (u'{0} [{1.institution}, {1.kind_name}] '
                u'{1.name!r}, {1.email!r}, {1.phone!r}, {1.other_info!r}'
                .format('-' if self.delete_rep else '+',
                        self))
