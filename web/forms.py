import re

from django import forms
from django.utils.translation import ugettext as _


HOUSE_NUMBER_RE = re.compile(r'^\s*\d+\w?\s*$')


def validate_house_number(string):
    match = HOUSE_NUMBER_RE.match(string)
    if not match:
        raise forms.ValidationError(
            _('A house number must be numeric and can contain at most one letter.'))


class HouseNumberForm(forms.Form):
    house_number = forms.CharField(label=_("Your house number"),
                                   validators=[validate_house_number])


class FeedbackForm(forms.Form):
    name = forms.CharField(label=_("Your name"),
                           required=True)
    email = forms.EmailField(label=_("Your e-mail address"),
                             required=True)
    subject = forms.CharField(label=_("Subject"),
                              max_length=100)
    message = forms.CharField(label=_("Message"),
                              widget=forms.widgets.Textarea(),
                              required=True)
