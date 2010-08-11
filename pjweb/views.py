#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django import forms
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response
from parasykjiems.contactdb.models import PollingDistrictStreet, Constituency, ParliamentMember, HierarchicalGeoData, MunicipalityMember, CivilParishMember
from pjutils.address_search import AddressSearch
from django.utils.translation import ugettext as _
from parasykjiems.pjweb.models import Email
from haystack.query import SearchQuerySet
from haystack.views import SearchView

class ContactForm(forms.Form):
    sender_name = forms.CharField(max_length=128)
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
    sender = forms.EmailField()

class IndexForm(forms.Form):
    address = forms.CharField(max_length=255)

class PrivateForm(forms.Form):
    private = forms.BooleanField()

def index(request):
    a_s = AddressSearch()
    query_string = ' '
    found_entries = None
    found_geodata = None
    all_mps = ParliamentMember.objects.all()
    if request.method == 'POST':
        form = IndexForm(request.POST)
        if form.is_valid():
            query_string = form.cleaned_data['address']
        else:
            query_string = '*'
	
        entry_query = a_s.get_query(query_string, ['street', 'city', 'district'])

        entry_query1 = a_s.get_query(query_string, ['name'])
        found_entries = PollingDistrictStreet.objects.filter(entry_query).order_by('street')
        found_geodata = HierarchicalGeoData.objects.filter(entry_query1).order_by('name')
#        found_entries = SearchQuerySet().auto_query(query_string)
        if not found_entries:
            found_by_index = SearchQuerySet().auto_query(query_string)
            if not found_by_index:
                suggestion = found_by_index.spelling_suggestion()
                print 'suggest', suggestion
                entry_query = a_s.get_query(suggestion, ['street', 'city', 'district'])
            #found_entries = SearchQuerySet().auto_query(suggestion)
                found_entries = PollingDistrictStreet.objects.filter(entry_query).order_by('street')
            else:
                found_entries = found_by_index

    else:
        form = IndexForm()
    return render_to_response('pjweb/index.html', {
        'all_mps': all_mps,
        'form': form,
        'entered': query_string,
        'found_entries': found_entries,
        'found_geodata': found_geodata,
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
    
def thanks(request, mtype, mp_id, private=None):
    parliament_member = ParliamentMember.objects.all().filter(
                id__exact=mp_id
            )
    ThanksMessage = _('Thank you. You will be informed, when %(name)s %(surname)s get the message.') % {
        'name':parliament_member[0].name, 'surname':parliament_member[0].surname
    }
    return render_to_response('pjweb/thanks.html', {
        'ThanksMessage': ThanksMessage,
    })

def smtp_error(request, mtype, mp_id, private=None):
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

def select_privacy(request, mtype, mp_id):
    parliament_member = ParliamentMember.objects.all().filter(
                id__exact=mp_id
            )
    form = PrivateForm(request.POST)
    
    return render_to_response('pjweb/private.html', {
        #'privacy': privacy,
        'mp_id': mp_id,
        'mtype': mtype,
        'form': form,
    })

def constituency(request, constituency_id):
    constituencies = Constituency.objects.all().filter(
                id__exact=constituency_id
            )
    parliament_members = ParliamentMember.objects.all().filter(
                constituency__exact=constituency_id
            )
    municipalities = HierarchicalGeoData.objects.all().filter(
                id__exact=constituency_id
            )
    if municipalities[0].type=='CivilParish':
        municipalities = HierarchicalGeoData.objects.all().filter(
                id__exact=municipalities[0].parent.id
            )

    civilparishes = HierarchicalGeoData.objects.all().filter(
                id__exact=constituency_id
            )

    municipality_members = MunicipalityMember.objects.all().filter(
                municipality__exact=municipalities[0].id
            )
    if not municipality_members:
        municipality_members = MunicipalityMember.objects.all().filter(
                municipality__exact=municipalities[0].parent.id
            )
    civilparish_members = CivilParishMember.objects.all().filter(
                civilParish__exact=constituency_id
            )

    return render_to_response('pjweb/const.html', {
        'constituencies': constituencies,
        'municipalities': municipalities,
        'civilparishes': civilparishes,
        'parliament_members': parliament_members,
        'municipality_members': municipality_members,
        'civilparish_members': civilparish_members,
    })
    
def contact(request, mtype, mp_id, private=None):
    if mtype=='mp':    
        receiver = ParliamentMember.objects.all().filter(
                id__exact=mp_id
            )
    elif mtype=='mn':
    	  receiver = MunicipalityMember.objects.all().filter(
                id__exact=mp_id
            )
    elif mtype=='cp':
    	  receiver = CivilParishMember.objects.all().filter(
                id__exact=mp_id
            )
            
    if not receiver[0].email:
        return HttpResponseRedirect('no_email')
        
    if private==None:
        return HttpResponseRedirect('select_privacy')
    elif private=='private':
        print 'Privatus'
    else:
        print 'Viešas'

    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            sender_name = form.cleaned_data['sender_name']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            sender = form.cleaned_data['sender']
            recipients = [receiver[0].email]
            #print recipients[0]
            if not recipients[0]:
                return HttpResponseRedirect('no_email')
            else:
                #from django.core.mail import send_mail
                #try:
                mail = Email(
                    sender_name = sender_name,
                    sender = sender,
                    recipient = recipients[0],
                    subject = subject,
                    message = message,
                    msg_state = 'W',
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
        'mtype': mtype,
        'private': private,
    })

