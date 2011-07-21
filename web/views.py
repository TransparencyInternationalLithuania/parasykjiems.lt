from django.shortcuts import render
from django.utils.translation import ugettext as _

def index(request):
    return render(request, 'index.html', {
        'search_query': request.GET.get('q', ''),
        'active_menu': _('Find representative'),
    })

def mail(request):
    return render(request, 'mail.html', {
        'active_menu': _('Public letters'),
    })

def about(request):
    return render(request, 'about.html', {
        'active_menu': _('About project'),
    })
