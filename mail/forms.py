from django import forms
from django.forms import widgets
from django.utils.translation import ugettext as _
import settings


class WriteLetterForm(forms.Form):
    name = forms.CharField(label=_("Your full name"),
                           help_text=_("You should enter your full name "
                                       "without abbreviations."),
                           required=True)

    email = forms.EmailField(
        label=_("Your e-mail address"),
        required=True,
        error_messages={
            'required': _("An e-mail address is required."),
            'invalid': _("Enter a valid e-mail address."),
        })
    if settings.DEBUG:
        # Allow entering @localhost emails when debugging.
        email.validators = []

    subject = forms.CharField(label=_("Subject"),
                              max_length=100,
                              required=True)

    is_open = forms.BooleanField(
        label=_("Open letter, which is visible to all visitors of the "
                "web site"),
        required=False)

    body = forms.CharField(label=_("Message"),
                           widget=forms.widgets.Textarea(),
                           required=True)

    choice_state = forms.CharField(widget=widgets.HiddenInput())
