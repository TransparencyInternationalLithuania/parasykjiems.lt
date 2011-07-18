from django.db import models
from django.utils.translation import ugettext_lazy as _

_NAME_LEN = 200


class InstitutionType(models.Model):
    """Represents a kind of institution for categorization.

    Allows easier abstraction of various kinds of institutions.
    """

    name = models.CharField(
        max_length=_NAME_LEN,
        help_text=_('Generic name for this kind of institution.'))
    
    representative_title = models.CharField(
        max_length=_NAME_LEN,
        help_text=_('Title of a corresponding representative.'))

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'institution types'


class Representative(models.Model):
    """Represents a person together with an institution.

    Contains all the related contact information.
    """

    full_name = models.CharField(max_length=_NAME_LEN)

    institution_name = models.CharField(
        max_length=_NAME_LEN,
        help_text=_('Specific name of the institution.'))
    
    institution_type = models.ForeignKey(InstitutionType)

    email = models.EmailField(help_text=_('Primary email.'))
    phone = models.CharField(max_length=50, blank=True)
    contact_info = models.TextField(
        blank=True,
        help_text=_('Other contact information, like address.'))
    
    def __unicode__(self):
        return u'%s %s' % (self.institution_type.representative_title,
                           self.full_name)

    def get_absolute_url(self):
        return '/representative/%d' % self.id
