# Create your views here.
from django import forms
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response
from parasykjiems.contactdb.models import PollingDistrictStreet, Constituency, ParliamentMember
from pjutils.address_search import AddressSearch
from django.utils.translation import ugettext as _
from parasykjiems.pjweb.models import Emails

class ContactForm(forms.Form):
    sender_name = forms.CharField(max_length=128)
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
    sender = forms.EmailField()

class IndexForm(forms.Form):
    address = forms.CharField(max_length=255)

def index(request):
    entered = ''
    suggestions = []
    a_s = AddressSearch()
    all_mps = ParliamentMember.objects.all()
    if request.method == 'POST':
        form = IndexForm(request.POST)
        if form.is_valid():
            entered = form.cleaned_data['address']
            suggestions = a_s.get_addr_suggests(PollingDistrictStreet, entered)
        if not suggestions:
            entered = _('Street, City and District have to be separated with ","')
    else:
        form = IndexForm()
    return render_to_response('pjweb/index.html', {
        'all_mps': all_mps,
        'form': form,
        'entered': entered,
        'suggestions': suggestions,
    })

def no_email(request, mp_id):
    parliament_member = ParliamentMember.objects.all().filter(
                id__exact=mp_id
            )
    NoEmailMsg = _('%(name)s %(surname)s email cannot be found in database.') % {
        'name':parliament_member[0].name, 'surname':parliament_member[0].surname
    }
    return render_to_response('pjweb/no_email.html', {
        'NoEmailMsg': NoEmailMsg,
    })
    
def thanks(request, mp_id):
    parliament_member = ParliamentMember.objects.all().filter(
                id__exact=mp_id
            )
    ThanksMessage = _('Thank you. Your email to %(name)s %(surname)s has been sent.') % {
        'name':parliament_member[0].name, 'surname':parliament_member[0].surname
    }
    return render_to_response('pjweb/thanks.html', {
        'ThanksMessage': ThanksMessage,
    })

def smtp_error(request, mp_id):
    parliament_member = ParliamentMember.objects.all().filter(
                id__exact=mp_id
            )
    ErrorMessage = _(
        'Problem occurred. Your Email to %(name)s %(surname)s has not been sent. Please try again later.'
    ) % {
        'name':parliament_member[0].name, 'surname':parliament_member[0].surname
    }
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
    parliament_member = ParliamentMember.objects.all().filter(
                id__exact=mp_id
            )

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            sender_name = form.cleaned_data['sender_name']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']
            recipients = [parliament_member[0].email]
            #print recipients[0]
            if not recipients[0]:
                return HttpResponseRedirect('no_email')
            else:
                #from django.core.mail import send_mail
                #try:
                mail = Emails(
                    sender_name = sender_name,
                    sender = sender,
                    recipient = recipients[0],
                    subject = subject,
                    message = message,
                    state = 'W',
                )
                print mail
                mail.save()
                    #sendmail = send_mail(subject, message, sender, recipients)
                #except:
                #    return HttpResponseRedirect('smtp_error')
            return HttpResponseRedirect('thanks')
    else:
        form = ContactForm()

    return render_to_response('pjweb/contact.html', {
        'form': form,
        'mp_id': mp_id,
    })
