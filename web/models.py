from django.db import models
from django.utils.translation import ugettext_lazy as _

_NAME_LEN = 200


class InstitutionType(models.Model):
    """A kind of institution for categorization.

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
    """A person together with an institution.

    Contains all the related contact information.
    """

    full_name = models.CharField(max_length=_NAME_LEN)

    institution_name = models.CharField(
        max_length=_NAME_LEN,
        help_text=_('Specific name of the institution.'))
    
    institution_type = models.ForeignKey(InstitutionType)

    email = models.EmailField(help_text=_('Primary email.'), blank=True)
    contact_info = models.TextField(
        blank=True,
        help_text=_('Other contact information, like address.'))
    
    def __unicode__(self):
        return u'%s %s' % (self.institution_type.representative_title,
                           self.full_name)

    def get_absolute_url(self):
        return '/person/%d' % self.id


class Territory(models.Model):
    """A street with relevant house numbers and the corresponding
    representative.

    Used to find representative by address.
    """

    NUMBER_FILTER_CHOICES = (
        ('all', _('all')),
        ('odd', _('odd')),
        ('even', _('even')),
    )

    municipality = models.CharField(max_length=_NAME_LEN)
    elderate = models.CharField(max_length=_NAME_LEN)
    city = models.CharField(max_length=_NAME_LEN)
    street = models.CharField(max_length=_NAME_LEN)

    number_from = models.IntegerField()
    number_from_letters = models.CharField(
        max_length=5,
        blank=True,
        help_text=_('Letters after the number_from house number.'))
    
    number_to = models.IntegerField()
    number_to_letters = models.CharField(
        max_length=5,
        blank=True,
        help_text=_('Letters after the number_to house number.'))
    
    number_filter = models.CharField(max_length=4,
                                     choices=NUMBER_FILTER_CHOICES)

    representative = models.ForeignKey(Representative)

    def __unicode__(self):
        return u', '.join(unicode(x) for x in [self.municipality,
                                               self.elderate,
                                               self.city,
                                               self.street,
                                               self.number_from,
                                               self.number_to,
                                               self.number_filter])

    class Meta:
        verbose_name_plural = _("territories")
