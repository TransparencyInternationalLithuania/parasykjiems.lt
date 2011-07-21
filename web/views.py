from django.shortcuts import render

def index(request):
    return render(request, 'index.html')

def mail(request):
    return render(request, 'mail.html')

def about(request):
    return render(request, 'about.html')
