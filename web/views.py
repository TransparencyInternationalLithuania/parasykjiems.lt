# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from forms import FeedbackForm
from models import Article
import settings


def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            body = render_to_string('mail/feedback.txt', {
                'form_data': form.cleaned_data,
                'ip': request.META['REMOTE_ADDR'],
            })

            user_address = u'{name} <{email}>'.format(**form.cleaned_data)

            EmailMessage(
                from_email=settings.SERVER_EMAIL,
                to=[settings.FEEDBACK_EMAIL],
                subject=(u'[ParašykJiems] ' +
                         _(u'Feedback from {}'.format(user_address))),
                body=body,
                headers={'Reply-To': user_address},
            ).send()
            return redirect(reverse(feedback_thanks))
    else:
        form = FeedbackForm()

    return render(request, 'views/feedback.html', {
        'form': form,
    })


def feedback_thanks(request):
    return render(request, 'views/feedback_thanks.html')


def setlang(request, language):
    request.session['django_language'] = language
    return redirect(request.META.get('HTTP_REFERER', '/'))


def article(request, location):
    art = get_object_or_404(Article, location=location)
    return render(request, 'views/article.html', {
        'article': art,
    })
