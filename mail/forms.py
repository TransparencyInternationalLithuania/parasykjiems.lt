from django import forms
from django.utils.translation import ugettext as _


class WriteLetterForm(forms.Form):
    name = forms.CharField(label=_("Your name"),
                           required=True)
    email = forms.EmailField(label=_("Your e-mail address"),
                             required=True)
    subject = forms.CharField(label=_("Subject"),
                              max_length=100,
                              required=True)
    body = forms.CharField(label=_("Message"),
                           widget=forms.widgets.Textarea(),
                           required=True)
    is_open = forms.BooleanField(label=_("Write an open letter"))
