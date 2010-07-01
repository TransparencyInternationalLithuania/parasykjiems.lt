# Create your views here.
from django import forms
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from parasykjiems.contactdb.models import PollingDistrictStreet, Constituency, ParliamentMember
from pjutils.address_search import AddressSearch

class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
    sender = forms.EmailField()

class IndexForm(forms.Form):
    address = forms.CharField(max_length=255)

def index(request):
    entered = ''
    suggestions = []
    a_s = AddressSearch()
    if request.method == 'POST':
        form = IndexForm(request.POST)
        if form.is_valid():
            entered = form.cleaned_data['address']
            suggestions = a_s.get_addr_suggests(PollingDistrictStreet, entered)
        if not suggestions:
            entered = 'Street, City and District have to be separated with ","'
    else:
        form = IndexForm()
    return render_to_response('pjweb/index.html', {
        'form': form,
        'entered': entered,
        'suggestions': suggestions,
    })

def thanks(request):    
    return HttpResponse("Thank you. Your email has been sent.")

def smtp_error(request):
    ErrorMessage = 'Problem, when trying to send Email. Please try again later.'
    return render_to_response('pjweb/error.html', {
        'ErrorMessage': ErrorMessage,
    })

def constituency(request, constituency_id):
    constituencies = Constituency.objects.all().filter(
                id__exact=constituency_id
            )
    parliament_members = ParliamentMember.objects.all().filter(
                constituency__exact=constituency_id
            )
    return render_to_response('pjweb/const.html', {
        'constituencies': constituencies,
        'parliament_members': parliament_members,
    })
    
def contact(request, mp_id):
    parliament_members = ParliamentMember.objects.all().filter(
                id__exact=mp_id
            )
    if request.method == 'POST': # If the form has been submitted...
        form = ContactForm(request.POST) # A form bound to the POST data
        if form.is_valid():
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']
            recipients = ['test@test.lt']

            from django.core.mail import send_mail
            try:
                sendmail = send_mail(subject, message, sender, recipients)
            except:
                return HttpResponseRedirect('smtp_error')
            return HttpResponseRedirect('thanks') # Redirect after POST
    else:
        form = ContactForm() # An unbound form

    return render_to_response('pjweb/contact.html', {
        'form': form,
    })
