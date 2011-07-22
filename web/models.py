from django.db import models
from django.utils.translation import ugettext_lazy as _

_NAME_LEN = 200


class InstitutionKind(models.Model):
    name = models.CharField(max_length=_NAME_LEN)
    description = models.TextField()

    def __unicode__(self):
        return self.name


class Institution(models.Model):
    name = models.CharField(max_length=_NAME_LEN)
    kind = models.ForeignKey(InstitutionKind)

    email = models.CharField(max_length=_NAME_LEN, blank=True)
    phone = models.CharField(max_length=_NAME_LEN, blank=True)
    address = models.TextField(blank=True)

    def __unicode__(self):
        return self.name


class RepresentativeKind(models.Model):
    """Kind of position of representative in institution."""
    name = models.CharField(max_length=_NAME_LEN)
    description = models.TextField()

    def __unicode__(self):
        return self.name


class Representative(models.Model):
    """A person together with an institution.

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

    
class Territory(models.Model):
    """A street with relevant house numbers and the corresponding
    representative.

    Used to find representative by address.
    """

    institution = models.ForeignKey(Institution)

    municipality = models.CharField(max_length=_NAME_LEN)
    city = models.CharField(max_length=_NAME_LEN,
                            help_text=_("Name of city, town or village."))
    street = models.CharField(max_length=_NAME_LEN, blank=True)

    numbers = models.TextField()

    def __unicode__(self):
        s = u'{}, {}'.format(self.municipality, self.city)
        if self.street != u'':
            s += u', {}'.format(self.street)
        s += u' [{}] -> {}'.format(self.numbers, self.institution)
        return s

    class Meta:
        verbose_name_plural = _("territories")
