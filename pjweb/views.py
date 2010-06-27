# Create your views here.
from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from parasykjiems.contactdb.models import CountyStreet, County, ParliamentMember

class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField()
    sender = forms.EmailField()

class IndexForm(forms.Form):
    address = forms.CharField(max_length=255)

def index(request):
    entered = ''
    suggestions = []
    if request.method == 'POST':
        form = IndexForm(request.POST)
        if form.is_valid():
            entered = form.cleaned_data['address']
        entered_list = entered.split(', ')
        if len(entered_list)>1:
            entered_street = entered_list[0].split(' ')
            filtered_addr = CountyStreet.objects.all().filter(
                city__startswith=entered_list[1],
                street__startswith=entered_street[0]
            )
            if not filtered_addr:
                entered_street = entered_list[1].split(' ')
                filtered_addr = CountyStreet.objects.all().filter(
                    city__startswith=entered_list[0],
                    street__startswith=entered_street[0]
                )
        else:
            entered_street = entered_list[0].split(' ')
            filtered_addr = CountyStreet.objects.all().filter(
                street__startswith=entered_street[0]
            )
        for entry in filtered_addr:
            entry_string = '%s, %s, %s' %(entry.street, entry.city, entry.district)
            suggestions.append(entry_string)
    else:
        form = IndexForm()
    return render_to_response('pjweb/index.html', {
        'form': form,
        'entered': entered,
        'suggestions': suggestions,
    })
#    return HttpResponse("Hello, world. You're at the index.")

def thanks(request):    
    return HttpResponse("Thank you. Your email has been sent.")

def smtp_error(request):    
    return HttpResponse("There was a problem, trying to send email. Is smtp configured?")

def contact(request):
    if request.method == 'POST': # If the form has been submitted...
        form = ContactForm(request.POST) # A form bound to the POST data
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']

            recipients = ['test@test.lt']

            from django.core.mail import send_mail
            try:
                send_mail(subject, message, sender, recipients)
            except:
                return HttpResponseRedirect('smtp_error')
            return HttpResponseRedirect('thanks') # Redirect after POST
    else:
        form = ContactForm() # An unbound form

    return render_to_response('pjweb/contact.html', {
        'form': form,
    })
