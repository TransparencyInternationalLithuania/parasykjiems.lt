from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist
import django.http
from haystack.query import SearchQuerySet

from web.models import Representative, Institution, Location, Territory
from web.forms import FeedbackForm
import web.house_numbers


def index(request):
    if 'q' in request.GET and request.GET['q'] != '':
        q = request.GET['q']
        results = SearchQuerySet().auto_query(q)
    else:
        q = ''
        results = []

    return render(request, 'index.html', {
        'search_query': q,
        'results': results,
        'active_menu': _('Representative search'),
    })


def letters(request):
    return render(request, 'letters.html', {
        'active_menu': _('Public letters'),
    })


def about(request):
    return render(request, 'about.html', {
        'active_menu': _('About project'),
    })


def representative(request, rep_id):
    try:
        rep = Representative.objects.get(id=rep_id)
        return render(request, 'representative.html', {
            'representative': rep,
            'active_menu': _('Representative search'),
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
            'active_menu': _('Representative search'),
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
                return render(request, 'house_number.html', {
                    'active_menu': _('Representative search'),
                })
        institutions = [t.institution for t in territories]
        return render(request, 'location.html', {
            'institutions': institutions,
            'active_menu': _('Representative search'),
        })

    except ObjectDoesNotExist:
        return django.http.HttpResponseNotFound(_('Location not found'))


def feedback(request):
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            # TODO: Actually send email.
            return render(request, 'feedback.html', {
                'active_menu': _('Feedback'),
            })
    else:
        form = FeedbackForm()

    return render(request, 'feedback.html', {
        'form': form,
        'active_menu': _('Feedback'),
    })


def setlang(request):
    language = request.GET.get('lang', 'lt')
    back = request.META.get('HTTP_REFERER', '/')
    response = django.http.HttpResponseRedirect(back)
    request.session['django_language'] = language
    return response
