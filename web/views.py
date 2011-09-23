# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _
from django.views.decorators.cache import cache_control

from forms import ContactForm
from models import Article
import settings


@cache_control(public=False)
def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            user_address = u'{name} <{email}>'.format(**form.cleaned_data)

            EmailMessage(
                from_email=settings.SERVER_EMAIL,
                to=[settings.FEEDBACK_EMAIL],
                subject=(u'[ParašykJiems] ' +
                         _(u'Feedback from {}').format(user_address)),
                body=form.cleaned_data['message'],
                headers={'Reply-To': user_address},
            ).send()
            return redirect(reverse(contact_thanks))
    else:
        form = ContactForm()

    return render(request, 'views/contact.html', {
        'form': form,
    })


@cache_control(max_age=60 * 60, public=True)
def contact_thanks(request):
    return render(request, 'views/contact_thanks.html')


@cache_control(max_age=60 * 60 * 24 * 7, public=True)
def robots_txt(request):
    # The actual content of robots.txt depends on
    # settings.TESTING_VERSION. The testing version disallows /.
    return render(request, 'robots.txt', content_type='text/plain')


@cache_control(max_age=60 * 60, public=True)
def article(request, location):
    art = get_object_or_404(Article, location=location)
    return render(request, 'views/article.html', {
        'article': art,
    })
