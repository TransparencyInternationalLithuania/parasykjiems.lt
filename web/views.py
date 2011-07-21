from django.shortcuts import render

def index(request):
    return render(request, 'index.html', {
        'search_query': request.GET.get('q', ''),
    })

def mail(request):
    return render(request, 'mail.html')

def about(request):
    return render(request, 'about.html')
