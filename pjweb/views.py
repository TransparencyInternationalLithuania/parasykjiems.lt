#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from django import forms
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _
from haystack.query import SearchQuerySet
from haystack.views import SearchView
from django.core.mail import send_mail
from parasykjiems.contactdb.models import PollingDistrictStreet, Constituency, ParliamentMember, HierarchicalGeoData, MunicipalityMember, CivilParishMember, SeniunaitijaMember
from parasykjiems.pjweb.models import Email
from pjutils.address_search import AddressSearch

class ContactForm(forms.Form):
    pub_choices = (
        ('',''),
        ('private','Private'),
        ('public','Public'),
    )
    public = forms.ChoiceField(choices = pub_choices)
    sender_name = forms.CharField(max_length=128)
    phone = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)
    sender = forms.EmailField()

class IndexForm(forms.Form):
    address_input = forms.CharField(max_length=255)

class PrivateForm(forms.Form):
    private = forms.BooleanField()
    
def get_rep(rep_id, rtype):
    if rtype=='mp':    
        receiver = ParliamentMember.objects.all().filter(
                id__exact=rep_id
            )
    elif rtype=='mn':
        receiver = MunicipalityMember.objects.all().filter(
                id__exact=rep_id
            )
    elif rtype=='cp':
        receiver = CivilParishMember.objects.all().filter(
                id__exact=rep_id
            )
    elif rtype=='sn':
        receiver = SeniunaitijaMember.objects.all().filter(
                id__exact=rep_id
            )

    return receiver[0]

def index(request):
    a_s = AddressSearch()
    query_string = ' '
    found_entries = None
    found_geodata = None
    suggestion = ''
    entry_query = ''
    entry_query1 = ''
    all_mps = ParliamentMember.objects.all()
    if request.method == 'POST':
        form = IndexForm(request.POST)
        if form.is_valid():
            query_string = form.cleaned_data['address_input']
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
                print 'sugg',suggestion
                logging.debug('suggestion:', suggestion)
                entry_query = a_s.get_query(suggestion, ['street', 'city', 'district'])
                #found_entries = SearchQuerySet().auto_query(suggestion)
                if entry_query:
                    found_entries = PollingDistrictStreet.objects.filter(entry_query).order_by('street')
                else:
                    found_entries = {}
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
        'step1': 'step1_active.png',
        'step2': 'step2_inactive.png',
        'step3': 'step3_inactive.png',
    })

def no_email(request, rtype, mp_id):
    parliament_member = ParliamentMember.objects.all().filter(
                id__exact=mp_id
            )
    NoEmailMsg = _('%(name)s %(surname)s email cannot be found in database.') % {
        'name':parliament_member[0].name, 'surname':parliament_member[0].surname
    }
    logging.debug('%s' % (NoEmailMsg))
    return render_to_response('pjweb/no_email.html', {
        'NoEmailMsg': NoEmailMsg,
        'step1': 'step1_inactive.png',
        'step2': 'step2_active.png',
        'step3': 'step3_inactive.png',
    })

def public_mails(request):
    all_mails = Email.objects.all().filter(public__exact=True)

    return render_to_response('pjweb/public_mails.html', {
        'all_mails': all_mails,
        'step1': 'step1_active.png',
        'step2': 'step2_inactive.png',
        'step3': 'step3_inactive.png',
    })

def public(request, mail_id):
    mails = Email.objects.all().filter(id__exact=mail_id)
    mail = mails[0]
    return render_to_response('pjweb/public.html', {
        'mail': mail,
        'step1': 'step1_inactive.png',
        'step2': 'step2_active.png',
        'step3': 'step3_inactive.png',
    })

def thanks(request, rtype, mp_id, private=None):
    receiver = get_rep(mp_id, rtype)

    ThanksMessage = _('Thank you. Your message to %(name)s %(surname)s has been sent.') % {
        'name':receiver.name, 'surname':receiver.surname
    }
    logging.debug('%s' % (ThanksMessage))
    return render_to_response('pjweb/thanks.html', {
        'ThanksMessage': ThanksMessage,
        'step1': 'step1_inactive.png',
        'step2': 'step2_inactive.png',
        'step3': 'step3_active.png',
    })

def smtp_error(request, rtype, mp_id, private=None):
    parliament_member = ParliamentMember.objects.all().filter(
                id__exact=mp_id
            )
    ErrorMessage = _(
        'Problem occurred. Your Email to %(name)s %(surname)s has not been sent. Please try again later.'
    ) % {
        'name':parliament_member[0].name, 'surname':parliament_member[0].surname
    }
    logging.debug('Error: %s' % (ErrorMessage))
    return render_to_response('pjweb/error.html', {
        'ErrorMessage': ErrorMessage,
        'step1': 'step1_inactive.png',
        'step2': 'step2_inactive.png',
        'step3': 'step3_active.png',
    })

def select_privacy(request, rtype, mp_id):
    logging.debug('Member type %s, member ID %s' % (rtype, mp_id))    
    parliament_member = ParliamentMember.objects.all().filter(
                id__exact=mp_id
            )
    form = PrivateForm(request.POST)
    
    return render_to_response('pjweb/private.html', {
        #'privacy': privacy,
        'mp_id': mp_id,
        'rtype': rtype,
        'form': form,
        'step1': 'step1_inactive.png',
        'step2': 'step2_active.png',
        'step3': 'step3_inactive.png',
    })

def constituency(request, constituency_id, rtype):
    #print constituency_id
    constituencies = []
    parliament_members = []
    municipalities = []
    civilparishes = []
    municipality_members = []
    civilparish_members = []
    seniunaitija_members = []
    if rtype=='mp':
        constituencies = Constituency.objects.all().filter(
                    id__exact=constituency_id
                )
        parliament_members = ParliamentMember.objects.all().filter(
                    constituency__exact=constituency_id
                )
    elif rtype=='cp':
        municipalities = HierarchicalGeoData.objects.all().filter(
                    id__exact=constituency_id
                )
        if municipalities[0].type=='City':
            municipalities = HierarchicalGeoData.objects.all().filter(
                        id__exact=municipalities[0].parent.id
                    )
        if municipalities[0].type=='CivilParish':
            municipalities = HierarchicalGeoData.objects.all().filter(
                    id__exact=municipalities[0].parent.id
                )

        civilparishes = HierarchicalGeoData.objects.all().filter(
                    id__exact=constituency_id
                )
        if civilparishes[0].type=='City':
            civilparishes = HierarchicalGeoData.objects.all().filter(
                        id__exact=civilparishes[0].parent.id
                    )

        seniunaitijas = HierarchicalGeoData.objects.all().filter(
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
        seniunaitija_members = SeniunaitijaMember.objects.all().filter(
                    seniunaitija__exact=constituency_id
                )

    return render_to_response('pjweb/const.html', {
        'constituencies': constituencies,
        'municipalities': municipalities,
        'civilparishes': civilparishes,
        'parliament_members': parliament_members,
        'municipality_members': municipality_members,
        'civilparish_members': civilparish_members,
        'seniunaitija_members': seniunaitija_members,
        'step1': 'step1_active.png',
        'step2': 'step2_inactive.png',
        'step3': 'step3_inactive.png',
    })
    
def contact(request, rtype, mp_id):
    print rtype, mp_id
    receiver = get_rep(mp_id, rtype)
    print receiver
    if not receiver.email:
        return HttpResponseRedirect('no_email')

    if request.method == 'POST':
        form = ContactForm(data=request.POST)
        if form.is_valid():
            public = form.cleaned_data[u'public']
            if public=='public':
                publ = True
            else:
                publ = False
            sender_name = form.cleaned_data[u'sender_name']
            phone = form.cleaned_data[u'phone']
            message = form.cleaned_data[u'message']
            sender = form.cleaned_data[u'sender']
            #recipients = [receiver.email]
            recipients = [u'testinis@pashtas.lt']
            #print recipients[0]
            if not recipients[0]:
                logging.debug('%s has no email' % (receiver.name, receiver.surname))
                return HttpResponseRedirect('no_email')
            else:
                #from django.core.mail import send_mail
                #try:
                mail = Email(
                    sender_name = sender_name,
                    sender = sender,
                    recipient = recipients[0],
                    phone = phone,
                    message = message,
                    msg_state = 'W',
                    public = publ,
                )
                
                sendmail = send_mail('', message, sender, recipients)
                #print 'email sent', sendmail
                if publ:
                    mail.save()
                    #print 'public mail saved'
                #except:
                #    return HttpResponseRedirect('smtp_error')
            return HttpResponseRedirect('thanks')
    else:
        form = ContactForm()
        
    return render_to_response('pjweb/contact.html', {
        'form': form,
        'mp_id': mp_id,
        'rtype': rtype,
        'representative': receiver,
        'step1': 'step1_inactive.png',
        'step2': 'step2_active.png',
        'step3': 'step3_inactive.png',
    })

