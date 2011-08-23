from django import forms
from django.utils.translation import ugettext as _


class FeedbackForm(forms.Form):
    name = forms.CharField(label=_("Your name"),
                           required=True)
    email = forms.EmailField(label=_("Your e-mail address"),
                             required=True)
    message = forms.CharField(label=_("Message"),
                              widget=forms.widgets.Textarea(),
                              required=True)
