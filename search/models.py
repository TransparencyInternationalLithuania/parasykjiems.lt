from django.db import models
from django.utils.translation import ugettext_lazy as _

_NAME_LEN = 200


class InstitutionKind(models.Model):
    name = models.CharField(max_length=_NAME_LEN)
    description = models.TextField()
    active = models.BooleanField()

    def __unicode__(self):
        return self.name


class Institution(models.Model):
    name = models.CharField(max_length=_NAME_LEN)
    kind = models.ForeignKey(InstitutionKind)

    email = models.CharField(max_length=_NAME_LEN, blank=True)
    phone = models.CharField(max_length=_NAME_LEN, blank=True)
    address = models.TextField(blank=True)

    def representatives(self):
        return Representative.objects.filter(institution=self)

    def __unicode__(self):
        return self.name

    @models.permalink
    def get_absolute_url(self):
        return ('institution', [self.id])


class RepresentativeKind(models.Model):
    """Kind of position of representative in institution."""
    name = models.CharField(max_length=_NAME_LEN)
    description = models.TextField()
    active = models.BooleanField()

    def __unicode__(self):
        return self.name


class Representative(models.Model):
    """A person working in an institution.

    Contains all the related contact information.
    """

    name = models.CharField(max_length=_NAME_LEN)
    kind = models.ForeignKey(RepresentativeKind)

    institution = models.ForeignKey(Institution)

    email = models.CharField(max_length=_NAME_LEN, blank=True)
    phone = models.CharField(max_length=_NAME_LEN, blank=True)
    other_contacts = models.TextField(blank=True)

    def __unicode__(self):
        return u'{}, {} in {}'.format(
            self.name,
            self.kind,
            self.institution)

    @models.permalink
    def get_absolute_url(self):
        return ('representative', [self.id])


class Location(models.Model):
    """Represents either a street or a whole town/village (if the
    street field is empty).

    Is generated automatically from Territories with the
    update_locations command.
    """

    municipality = models.CharField(max_length=_NAME_LEN, db_index=True)
    elderate = models.CharField(max_length=_NAME_LEN,
                                blank=True,
                                db_index=True)
    city = models.CharField(max_length=_NAME_LEN,
                            db_index=True,
                            help_text=_("Name of city, town or village."))
    street = models.CharField(max_length=_NAME_LEN, blank=True, db_index=True)

    def __unicode__(self):
        s = u'{}, {}'.format(self.municipality, self.city)
        if self.street != u'':
            s += u', {}'.format(self.street)
        return s

    @models.permalink
    def get_absolute_url(self):
        return ('location', [self.id])


class Territory(models.Model):
    """A location with relevant house numbers and the corresponding
    representative.

    Used to find institutions by address.
    """

    municipality = models.CharField(max_length=_NAME_LEN, db_index=True)
    elderate = models.CharField(max_length=_NAME_LEN,
                                blank=True,
                                db_index=True)
    city = models.CharField(max_length=_NAME_LEN,
                            db_index=True,
                            help_text=_("Name of city, town or village."))
    street = models.CharField(max_length=_NAME_LEN, blank=True, db_index=True)

    institution = models.ForeignKey(Institution)
    numbers = models.TextField()

    def __unicode__(self):
        loc = u'{}, {}'.format(self.municipality, self.city)
        if self.street != u'':
            loc += u', {}'.format(self.street)

        return u'{} [{}] -> {}'.format(
            loc,
            self.numbers,
            self.institution)

    class Meta:
        verbose_name_plural = _("territories")