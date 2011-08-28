from django import forms
from django.forms import widgets
from django.utils.translation import ugettext as _
import settings


def validate_full_name(string):
    string = string.strip()

    if '.' in string:
        raise forms.ValidationError(
            _("You shouldn't abbreviate your name."))

    if ' ' not in string:
        raise forms.ValidationError(
            _("You should enter both your first name and your surname, "
              "separated by spaces."))


class WriteLetterForm(forms.Form):
    name = forms.CharField(label=_("Your full name"),
                           required=True,
                           validators=[validate_full_name])

    email = forms.EmailField(label=_("Your e-mail address"),
                             required=True)
    if settings.DEBUG:
        # Allow entering @localhost emails when debugging.
        email.validators = []

    subject = forms.CharField(label=_("Subject"),
                              max_length=100,
                              required=True)

    is_open = forms.BooleanField(
        label=_("Open letter"),
        required=False,
        help_text=_("An open letter is visible to everyone in the "
                    "letter list in the website."))

    body = forms.CharField(label=_("Message"),
                           widget=forms.widgets.Textarea(),
                           required=True)

    choice_state = forms.CharField(widget=widgets.HiddenInput())
