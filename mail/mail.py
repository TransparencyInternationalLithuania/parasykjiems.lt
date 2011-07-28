from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

import settings
import mail.models
import search.models

def submit_enquiry(from_name, from_email, to, subject, body, parent=None):
    enquiry = mail.models.Enquiry(
        from_name=from_name,
        from_email=from_email,
        subject=subject,
        body=body,
        parent=parent,
    )
    if isinstance(to, search.models.Representative):
        enquiry.representative = to
    else:
        enquiry.institution = to
    enquiry.save()

    # Send confirmation email.
    confirm_msg = render_to_string('mail/confirm.txt', {
        'confirm_url': reverse('confirm', [enquiry8.unique_hash]),
        'from_name': from_email,
    })
    send_mail(
        from_email=settings.SERVER_EMAIL,
        recipient_list=u'{} <{}>'.format(from_name, from_email),
        subject=_('Confirm your enquiry'),
        message=confirm_msg,
    )

    return enquiry
