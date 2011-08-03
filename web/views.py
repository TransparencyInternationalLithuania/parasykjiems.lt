from django.shortcuts import render, redirect
from django.template.loader import render_to_string
from django.core.mail import send_mail
from django.core.urlresolvers import reverse

from forms import FeedbackForm
import settings


def about(request):
    return render(request, 'views/about.html')


def help_view(request):
    return render(request, 'views/help.html')


def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            message = render_to_string('mail/feedback.txt', {
                'form_data': form.cleaned_data,
                'ip': request.META['REMOTE_ADDR'],
            })

            send_mail(
                from_email=u'{name} <{email}>'.format(**form.cleaned_data),
                subject=form.cleaned_data['subject'],
                message=message,
                recipient_list=[settings.FEEDBACK_EMAIL],
            )
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
