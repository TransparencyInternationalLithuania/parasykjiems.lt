from django.shortcuts import render
from django.utils.translation import ugettext as _
import django.http

def index(request):
    return render(request, 'index.html', {
        'search_query': request.GET.get('q', ''),
        'active_menu': _('Representative search'),
    })

def mail(request):
    return render(request, 'mail.html', {
        'active_menu': _('Public letters'),
    })

def about(request):
    return render(request, 'about.html', {
        'active_menu': _('About project'),
    })

def setlang(request):
    language = request.GET.get('lang', 'lt')
    back = request.META.get('HTTP_REFERER', '/')
    response = django.http.HttpResponseRedirect(back)
    request.session['django_language'] = language
    return response
