from django.db import models
from search.models import Representative, Institution, RepresentativeKind
from search.search_indexes import RepresentativeIndex
import slug


_NAME_LEN = 200


class RepresentativeChange(models.Model):
    # These fields are used for lookup.
    institution = models.ForeignKey(Institution)
    kind = models.ForeignKey(RepresentativeKind)

    # If this field is true, the change represents a deletion istead
    # of an update.
    delete_rep = models.BooleanField(default=False)

    multiple = models.BooleanField(default=False)

    # These fields may be None if they should be left unchanged on update.
    name = models.CharField(max_length=_NAME_LEN, null=True, default=None)
    email = models.CharField(max_length=_NAME_LEN, null=True, default=None)
    phone = models.CharField(max_length=_NAME_LEN, null=True, default=None)
    other_info = models.CharField(max_length=_NAME_LEN,
                                  null=True,
                                  default=None)

    def __init__(self, *args, **kwargs):
        super(RepresentativeChange, self).__init__(*args, **kwargs)
        if self.multiple:
            maybe_rep = Representative.objects.filter(
                institution=self.institution,
                kind=self.kind,
                name=self.name)
        else:
            maybe_rep = Representative.objects.filter(
                institution=self.institution,
                kind=self.kind)
        if maybe_rep.exists():
            self.rep = maybe_rep.get()
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
        return ((self.multiple and not self.rep) or
                self.name_changed() or self.phone_changed() or
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
        return (u'{0} [{1.institution.name}, {1.kind.name}] '
                u'{1.name!r}, {1.email!r}, {1.phone!r}, {1.other_info!r}'
                .format('-' if self.delete_rep else '+',
                        self))


class InstitutionChange(models.Model):
    institution = models.ForeignKey(Institution)

    # These fields may be None if they should be left unchanged on update.
    email = models.CharField(max_length=_NAME_LEN, null=True, default=None)
    phone = models.CharField(max_length=_NAME_LEN, null=True, default=None)
    other_info = models.TextField(null=True,
                                  default=None)
    address = models.TextField(null=True,
                               default=None)

    def phone_changed(self):
        return ((self.phone is not None) and
                (self.institution.phone != self.phone))

    def email_changed(self):
        return ((self.email is not None) and
                (self.institution.email != self.email))

    def other_info_changed(self):
        return ((self.other_info is not None) and
                (self.institution.other_info != self.other_info))

    def address_changed(self):
        return ((self.address is not None) and
                (self.institution.address != self.address))

    def changed(self):
        return (self.phone_changed() or
                self.email_changed() or
                self.other_info_changed() or
                self.address_changed())

    def apply_change(self):
        if self.phone is not None:
            self.institution.phone = self.phone
        if self.email is not None:
            self.institution.email = self.email
        if self.other_info is not None:
            self.institution.other_info = self.other_info
        if self.address is not None:
            self.institution.address = self.address
        self.institution.save()
        self.delete()

    def __unicode__(self):
        return (u'[{0.institution.name}] '
                u'{0.email!r}, {0.phone!r}, {0.other_info!r}'
                .format(self))
