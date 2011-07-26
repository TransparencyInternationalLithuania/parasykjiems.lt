from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import send_mail
import django.http
from haystack.query import SearchQuerySet
from django.template import Context, loader
from django.core.urlresolvers import reverse

import settings
from web.models import Representative, Institution, Location, Territory
from web.forms import FeedbackForm
import web.house_numbers


def search(request):
    if 'q' in request.GET and request.GET['q'] != '':
        q = request.GET['q']
        results = SearchQuerySet().auto_query(q)
    else:
        q = ''
        results = []

    return render(request, 'search.html', {
        'search_query': q,
        'results': results,
    })


def letters(request):
    return render(request, 'letters.html')


def about(request):
    return render(request, 'about.html')


def representative(request, rep_id):
    try:
        rep = Representative.objects.get(id=rep_id)
        return render(request, 'representative.html', {
            'representative': rep,
        })
    except ObjectDoesNotExist:
        return django.http.HttpResponseNotFound(_('Representative not found'))


def institution(request, inst_id):
    try:
        inst = Institution.objects.get(id=inst_id)
        reps = Representative.objects.filter(institution=inst)
        return render(request, 'institution.html', {
            'institution': inst,
            'representatives': reps,
        })
    except ObjectDoesNotExist:
        return django.http.HttpResponseNotFound(_('Institution not found'))


def location(request, loc_id, house_number=None):
    if 'house_number' in request.GET:
        return redirect('/location/{}/{}'.format(loc_id,
                                                 request.GET['house_number']))
    try:
        loc = Location.objects.get(id=loc_id)
        all_territories = Territory.objects.filter(location=loc)
        territories = list(all_territories.filter(numbers=''))
        restricted_territories = all_territories.exclude(numbers='')
        if restricted_territories.exists():
            if house_number:
                for rt in restricted_territories:
                    if web.house_numbers.territory_contains(rt, house_number):
                        territories.append(rt)
            else:
                return render(request, 'house_number.html')
        institutions = [t.institution for t in territories]
        return render(request, 'location.html', {
            'institutions': institutions,
        })

    except ObjectDoesNotExist:
        return django.http.HttpResponseNotFound(_('Location not found'))


def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            t = loader.get_template('mail/feedback.txt')
            message = t.render(Context({
                'form_data': form.cleaned_data,
                'ip': request.META['REMOTE_ADDR'],
            }))

            send_mail(
                from_email=u'{name} <{email}>'.format(**form.cleaned_data),
                subject=form.cleaned_data['subject'],
                message=message,
                recipient_list=[settings.FEEDBACK_EMAIL],
            )
            return redirect('/feedback/thanks')
    else:
        form = FeedbackForm()

    return render(request, 'feedback.html', {
        'form': form,
    })


def feedback_thanks(request):
    return render(request, 'thanks.html')


def setlang(request, language):
    request.session['django_language'] = language
    return redirect(request.META.get('HTTP_REFERER', '/'))
