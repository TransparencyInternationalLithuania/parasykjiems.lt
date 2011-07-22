from django.shortcuts import render
from django.utils.translation import ugettext as _
from django.core.exceptions import ObjectDoesNotExist
import django.http

from web.models import Representative, Institution

def index(request):
    return render(request, 'index.html', {
        'search_query': request.GET.get('q', ''),
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

def representative(request, id):
    try:
        rep = Representative.objects.get(id=id)
        return render(request, 'representative.html', {
            'representative': rep,
            'active_menu': _('Representative search'),
        })
    except ObjectDoesNotExist:
        return django.http.HttpResponseNotFound(_('Representative not found'))

def institution(request, id):
    try:
        inst = Institution.objects.get(id=id)
        reps = Representative.objects.filter(institution=inst)
        return render(request, 'institution.html', {
            'institution': inst,
            'representatives': reps,
            'active_menu': _('Representative search'),
        })
    except ObjectDoesNotExist:
        return django.http.HttpResponseNotFound(_('Institution not found'))

def setlang(request):
    language = request.GET.get('lang', 'lt')
    back = request.META.get('HTTP_REFERER', '/')
    response = django.http.HttpResponseRedirect(back)
    request.session['django_language'] = language
    return response
