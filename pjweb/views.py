#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import re
import settings
from django import forms
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _, ugettext_lazy, ungettext
#from haystack.query import SearchQuerySet
#from haystack.views import SearchView
from django.core.mail import send_mail, EmailMessage
from parasykjiems.pjweb.models import Email
from parasykjiems.pjweb.forms import *
from pjutils.address_search import AddressSearch
from django.utils import simplejson
import random
from django.contrib.sites.models import Site
from pjutils.uniconsole import *
from cdb_lt_municipality.models import MunicipalityMember, Municipality
from cdb_lt_mps.models import ParliamentMember, Constituency, PollingDistrictStreet
from cdb_lt_civilparish.models import CivilParishMember, CivilParishStreet
from cdb_lt_seniunaitija.models import SeniunaitijaMember, SeniunaitijaStreet
from cdb_lt_streets.models import HierarchicalGeoData, LithuanianStreetIndexes
from django.db.models.query_utils import Q, Q
from django.utils.encoding import iri_to_uri
from pjutils.deprecated import deprecated
from cdb_lt_streets.searchInIndex import searchInIndex, deduceAddress, removeGenericPartFromStreet, removeGenericPartFromMunicipality

logger = logging.getLogger(__name__)

def is_odd(number):
    if number%2==1:
        return True
    else:
        return False

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




def searchInStreetIndex(query_string):
    """ Searches throught street index and returns municipality / city / street/ house number
    Additionally returns more data for rendering in template"""

    logger.debug("query_string %s" % query_string)
    found_geodata = None
    not_found = ''

    addressContext = deduceAddress(query_string)
    found_entries = searchInIndex(addressContext)

    # attach house numbers
    number = None
    if (len(addressContext.number) > 0):
        number = addressContext.number[0]
    for f in found_entries:
        f.number = number
        if (f.number is not None):
            iri = "/pjweb/choose_rep/%s/%s/%s/%s/" % (f.municipality, f.city, f.street, f.number)
        elif (f.street is not None and f.street != u""):
            iri = "/pjweb/choose_rep/%s/%s/%s/" % (f.municipality, f.city, f.street)
        else:
            iri = "/pjweb/choose_rep/%s/%s/" % (f.municipality, f.city)
        uri = iri_to_uri(iri)
        f.url = uri


    for e in found_entries:
        print "%s %s %s %s %s" % (e.id, e.street, e.city, e.municipality, e.number)
    print "len %s " % len(found_entries)

    if not found_entries:
        found_entries = {}
        not_found = _('No addressess were found. Please refine your search. Or use feedback form to inform us about missing address')

    result = {
        'found_entries': found_entries,
        'found_geodata': found_geodata,
        'not_found': not_found,
    }
    return result




def addHouseNumberQuery(query, house_number):
    """ if house number is a numeric, add special conditions to check
    if house number is matched"""
    if (house_number is None):
        return query
    if (house_number.isdigit() == False):
        return query

    # convert to integer
    house_number = int(house_number)
    isOdd = house_number % 2
    query = query.filter(numberFrom__lte = house_number ) \
        .filter(numberTo__gte = house_number) \
        .filter(numberOdd = isOdd)
    return query




def findMPs(municipality = None, city = None, street = None, house_number = None):
    street = removeGenericPartFromStreet(street)
    municipality = removeGenericPartFromMunicipality(municipality)

    try:
        query = PollingDistrictStreet.objects.all().filter(municipality__contains = municipality)\
            .filter(street__contains = street) \
            .filter(city__contains = city)
        query = addHouseNumberQuery(query, house_number)

        query = query.distinct() \
            .values('constituency')
        idList = [p['constituency'] for p in query]
    except PollingDistrictStreet.DoesNotExist:
        logging.info("no polling district")
        return []

    members = ParliamentMember.objects.all().filter(constituency__in = idList)
    return members

def findMunicipalityMembers(municipality = None, city = None, street = None, house_number = None):

    try:
        query = Municipality.objects.all().filter(name__contains = municipality)

        query = query.distinct() \
            .values('id')
        idList = [p['id'] for p in query]
    except Municipality.DoesNotExist:
        logging.info("no municipalities found")
        return []

    members = MunicipalityMember.objects.all().filter(municipality__in = idList)
    return members

def findCivilParishMembers(municipality = None, city = None, street = None, house_number = None):
    street = removeGenericPartFromStreet(street)
    municipality = removeGenericPartFromMunicipality(municipality)

    try:
        query = CivilParishStreet.objects.all().filter(municipality__contains = municipality)\
            .filter(street__contains = street) \
            .filter(city__contains = city)

        query = query.distinct() \
            .values('civilParish')
        idList = [p['civilParish'] for p in query]
    except CivilParishStreet.DoesNotExist:
        logging.info("no civilParish")
        return []

    members = CivilParishMember.objects.all().filter(civilParish__in = idList)
    return members


def findSeniunaitijaMembers(municipality = None, city = None, street = None, house_number = None):
    street = removeGenericPartFromStreet(street)
    municipality = removeGenericPartFromMunicipality(municipality)

    query = SeniunaitijaStreet.objects.all().filter(municipality__contains = municipality)\
        .filter(street__contains = street) \
        .filter(city__contains = city)
    query = addHouseNumberQuery(query, house_number)

    query = query.distinct().values('seniunaitija')
    idList = [p['seniunaitija'] for p in query]

    if (len(idList) == 0):
        logging.debug("no seniunaitija street at first attempt")

        query = SeniunaitijaStreet.objects.all().filter(municipality__contains = municipality)\
            .filter(city__contains = city)


        query = query.distinct().values('seniunaitija')
        idList = [p['seniunaitija'] for p in query]

    if (len(idList) == 0):
        logging.debug("no seniunaitija street at second attempt")
        return []


    members = SeniunaitijaMember.objects.all().filter(seniunaitija__in = idList)
    return members

def choose_representative(request, municipality = None, city = None, street = None, house_number = None):
    print "municipality %s" % municipality
    print "city %s" % city
    print "street %s" % street
    print "house_number %s" % house_number

    parliament_members = findMPs(municipality, city, street, house_number)
    municipality_members = findMunicipalityMembers(municipality, city, street, house_number)
    civilparish_members = findCivilParishMembers(municipality, city, street, house_number)
    seniunaitija_members = findSeniunaitijaMembers(municipality, city, street, house_number)


    return render_to_response('pjweb/const.html', {
        'parliament_members': parliament_members,
        'municipality_members': municipality_members,
        'civilparish_members': civilparish_members,
        'seniunaitija_members': seniunaitija_members,
        'LANGUAGES': settings.LANGUAGES,
        'step1': 'step1_active.png',
        'step2': 'step2_inactive.png',
        'step3': 'step3_inactive.png',
    })

@deprecated
def get_civilparish(pd_id, constituency):

    district = constituency.district.split(' ')[0]

    parent_dstr = []
    parent_cp = []
    parent_city = []
    streets = []
    seniunaitijas = []
    civilparish = constituency.city[:-2]
    vard = [u'as', u'ai', u'is', u'us', u'ės', u'ė', u'a', u'ys']
    kilm = [u'o', u'ų', u'io', u'aus', u'ių', u'ės', u'os', u'ių']
    for gal in range(len(vard)):
        
        if constituency.city[-2:]==vard[gal]:
            civilparish = civilparish + kilm[gal]

    # search for municipality location
    if district==civilparish:
        # first try searching with adding a special term "miesto", since
        # in Lithuania there might exist data with similar words, e.g.:
        # "Vilniaus miesto seniūnija"
        # "Vilniaus rajono seniūnija"
        found_geodata = HierarchicalGeoData.objects.filter(
            name__icontains=district,
            type__exact='Municipality').filter(name__icontains='miesto')
    else:
        # if municipality location with "miesto' does not exist,
        # search the rest
        found_geodata = HierarchicalGeoData.objects.filter(
            name__icontains=district,
            type__exact='Municipality').exclude(name__icontains='miesto')

    for address in found_geodata:
        parent_dstr.append(address.id)

    civilparish = civilparish.strip()
    if civilparish:
        all_results = HierarchicalGeoData.objects.filter(
                name__icontains=civilparish,)
    else:
        all_results = {}

    for result in all_results:
        parent = result
        correct_dstr = False
        if parent.parent != None:
            while True:
                print parent.name
                if parent.type == 'Municipality' and parent.id == parent_dstr[0]:
                    correct_dstr = True
                parent = parent.parent
                if parent.parent == None:
                    break
        if correct_dstr:
            address = result
            while True:

                if address.type == 'Seniunaitija':
                    seniunaitijas.append(address.id)
                elif address.type == 'City':
                    parent_city.append(address.id)
                elif address.type == 'CivilParish':
                    parent_cp.append(address.id)
                elif address.type == 'Street':
                    streets.append(address.id)
                address = address.parent
                if address.parent == None:
                    break

    result = {
        'parent_dstr': parent_dstr,
        'parent_city': parent_city,
        'parent_cp': parent_cp,
        'streets': streets,
        'seniunaitijas': seniunaitijas,
    }
#    print result
    return result

def index(request):
    query_string = ' '
    entered = ''
    address = {
        'found_entries': None,
        'found_geodata': None,
        'not_found': '',
        }
    suggestion = ''

    if request.method == 'POST':
        form = IndexForm(request.POST)
        if form.is_valid():
            query_string = form.cleaned_data['address_input']
            entered = form.cleaned_data['address_input']
        else:
            query_string = ''
        address = searchInStreetIndex(query_string)
    else:
        form = IndexForm()

    if address['found_entries'] and len(address['found_entries'])==1:
        url = address['found_entries'][0].url
        return HttpResponseRedirect(url)
    else:
        return render_to_response('pjweb/index.html', {
            'form': form,
            'LANGUAGES': settings.LANGUAGES,
            'entered': query_string,
            'found_entries': address['found_entries'],
            'found_geodata': address['found_geodata'],
            'not_found': address['not_found'],
            'step1': 'step1_active.png',
            'step2': 'step2_inactive.png',
            'step3': 'step3_inactive.png',
        })

def no_email(request, rtype, mp_id):
    representative = get_rep(mp_id, rtype)
    NoEmailMsg = _('%(name)s %(surname)s email cannot be found in database.') % {
        'name':representative.name, 'surname':representative.surname
    }
    logger.debug('%s' % (NoEmailMsg))
    return render_to_response('pjweb/no_email.html', {
        'NoEmailMsg': NoEmailMsg,
        'LANGUAGES': settings.LANGUAGES,
        'step1': 'step1_inactive.png',
        'step2': 'step2_active.png',

        'step3': 'step3_inactive.png',
    })

def public_mails(request):
    all_mails = Email.objects.all().filter(public__exact=True)

    return render_to_response('pjweb/public_mails.html', {
        'all_mails': all_mails,
        'LANGUAGES': settings.LANGUAGES,
        'step1': 'step1_inactive.png',
        'step2': 'step2_inactive.png',
        'step3': 'step3_inactive.png',
    })

def about(request):
    return render_to_response('pjweb/about.html', {
        'LANGUAGES': settings.LANGUAGES,
        'step1': 'step1_inactive.png',
        'step2': 'step2_inactive.png',
        'step3': 'step3_inactive.png',
    })

def public(request, mail_id):
    mails = Email.objects.all().filter(id__exact=mail_id)
    mail = mails[0]
    return render_to_response('pjweb/public.html', {
        'mail': mail,
        'LANGUAGES': settings.LANGUAGES,
        'step1': 'step1_inactive.png',
        'step2': 'step2_active.png',
        'step3': 'step3_inactive.png',
    })

def smtp_error(request, rtype, mp_id, private=None):
    representative = get_rep(mp_id, rtype)
    ErrorMessage = _(
        'Problem occurred. Your Email to %(name)s %(surname)s has not been sent. Please try again later.'
    ) % {
        'name':representative.name, 'surname':representative.surname
    }
    logger.debug('Error: %s' % (ErrorMessage))
    return render_to_response('pjweb/error.html', {
        'ErrorMessage': ErrorMessage,
        'LANGUAGES': settings.LANGUAGES,
        'step1': 'step1_inactive.png',
        'step2': 'step2_inactive.png',
        'step3': 'step3_active.png',
    })

@deprecated
def constituency(request, pd_id):
    constituency = PollingDistrictStreet.objects.filter(id__exact=pd_id)[0]
    constituency_id = constituency.constituency_id
    address = get_civilparish(pd_id, constituency)
    parent_dstr = address['parent_dstr']
    parent_cp = address['parent_cp']
    parent_city = address['parent_city']
    streets = address['streets']
    seniunaitijas = address['seniunaitijas']

#    print found_geodata
    constituencies = []
    parliament_members = []
    municipalities = []
    civilparishes = []
    municipality_members = []
    civilparish_members = []
    seniunaitija_members = []

    constituencies = Constituency.objects.all().filter(
                id__exact=constituency_id
            )
    parliament_members = ParliamentMember.objects.all().filter(
                constituency__exact=constituency_id
            )

    municipalities = HierarchicalGeoData.objects.all().filter(
                id__in=parent_dstr
            )

    civilparishes = HierarchicalGeoData.objects.all().filter(
                id__in=parent_cp
            )

    seniunaitijas = HierarchicalGeoData.objects.all().filter(
                id__in=seniunaitijas
            )

    municipality_members = MunicipalityMember.objects.all().filter(
                municipality__in=parent_dstr
            )

    civilparish_members = CivilParishMember.objects.all().filter(
                civilParish__in=parent_cp
            )
    seniunaitija_members = SeniunaitijaMember.objects.all().filter(
                seniunaitija__in=seniunaitijas
            )

    return render_to_response('pjweb/const.html', {
        'constituencies': constituencies,
        'municipalities': municipalities,
        'civilparishes': civilparishes,
        'parliament_members': parliament_members,
        'municipality_members': municipality_members,
        'civilparish_members': civilparish_members,
        'seniunaitija_members': seniunaitija_members,
        'LANGUAGES': settings.LANGUAGES,
        'step1': 'step1_active.png',
        'step2': 'step2_inactive.png',
        'step3': 'step3_inactive.png',
    })
    
def contact(request, rtype, mp_id):
    receiver = get_rep(mp_id, rtype)
    if not receiver.email and not receiver.officeEmail:
        return HttpResponseRedirect('no_email')

    if request.method == 'POST':
        send = request.POST.has_key('send')
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
            answer_no = random.randrange(0, 10000),
            answer_no = answer_no[0]
            #recipients = [receiver.email, receiver.officeEmail]
            recipients = ['parasykjiems@gmail.com']
            if not recipients[0]:
                logger.debug('%s has no email' % (receiver.name, receiver.surname))
                return HttpResponseRedirect('no_email')
            else:
                #from django.core.mail import send_mail
                #try:
                mail = Email(
                    sender_name = sender_name,
                    sender = sender,
                    recipient_id = receiver.id,
                    recipient_type = rtype,
                    recipient_name = '%s %s' % (receiver.name, receiver.surname),
                    phone = phone,
                    message = message,
                    msg_state = 'W',
                    msg_type = 'M',
                    answer_no = answer_no,
                    public = publ,
                )
                if send:
                    if publ:
                        mail.save()
                        message = message + _('\nIf You want to response, click this link:')+'\nhttp://%s/response/%s/%s' % (
                            Site.objects.get_current().domain, mail.id, answer_no
                        )
                    email = EmailMessage(u'Gavote laišką nuo %s' % sender_name, message, sender,
                        recipients, [],
                        headers = {'Reply-To': sender})
                    email.send()
                    ThanksMessage = _('Thank you. Your message has been sent.')
                    logger.debug('%s' % (ThanksMessage))
                    return render_to_response('pjweb/thanks.html', {
                        'ThanksMessage': ThanksMessage,
                        'LANGUAGES': settings.LANGUAGES,
                        'step1': 'step1_inactive.png',
                        'step2': 'step2_inactive.png',
                        'step3': 'step3_active.png',
                    })
            if not send:
                return render_to_response('pjweb/preview.html', {
                    'form': form,
                    'mp_id': mp_id,
                    'rtype': rtype,
                    'preview': mail,
                    'msg_lst': message.split('\n'),
                    'representative': receiver,
                    'LANGUAGES': settings.LANGUAGES,
                    'step1': 'step1_inactive.png',
                    'step2': 'step2_inactive.png',
                    'step3': 'step3_active.png',
                })

    else:
        form = ContactForm(initial={'message': 'Gerb. p. %s, \n\n\n\nGeros dienos.' % receiver.name })
        
    return render_to_response('pjweb/contact.html', {
        'form': form,
        'mp_id': mp_id,
        'rtype': rtype,
        'representative': receiver,
        'LANGUAGES': settings.LANGUAGES,
        'step1': 'step1_inactive.png',
        'step2': 'step2_active.png',
        'step3': 'step3_inactive.png',
    })

def feedback(request):

    if request.method == 'POST':
        form = FeedbackForm(data=request.POST)
        if form.is_valid():
            message = form.cleaned_data[u'message']
            sender = 'Concerned citizen'
            recipients = ['parasykjiems@gmail.com']

            email = EmailMessage(u'Pastaba dėl parašykjiems.lt', message, sender,
                recipients, [])
            email.send()
            ThanksMessage = _('Thank you. Your message has been sent.')
            logger.debug('%s' % (ThanksMessage))
            return render_to_response('pjweb/thanks.html', {
                'ThanksMessage': ThanksMessage,
                'LANGUAGES': settings.LANGUAGES,
                'step1': 'step1_inactive.png',
                'step2': 'step2_inactive.png',
                'step3': 'step3_active.png',
            })

    else:
        form = FeedbackForm()
        
    return render_to_response('pjweb/feedback.html', {
        'form': form,
        'LANGUAGES': settings.LANGUAGES,
        'step1': 'step1_inactive.png',
        'step2': 'step2_inactive.png',
        'step3': 'step3_inactive.png',
    })

def response(request, mail_id, response_no):
    mails = Email.objects.all().filter(id__exact=mail_id)
    mail = mails[0]
    responder = get_rep(mail.recipient_id, mail.recipient_type)
    if int(mail.answer_no)==int(response_no) and request.method == 'POST':
        form = FeedbackForm(data=request.POST)
        if form.is_valid():
            message = form.cleaned_data[u'message']
            sender = responder.email
            recipients = mail.sender

            mail = Email(
                sender_name = mail.recipient_name,
                sender = responder.email,
                recipient_id = mail.recipient_id,
                recipient_type = mail.recipient_type,
                recipient_name = mail.sender_name,
                message = message,
                msg_state = 'R',
                msg_type = 'R',
                answer_no = response_no,
                public = True,
            )
            mail.save()
            ThanksMessage = _('Thank you. Your response has been posted.')
            logger.debug('%s' % (ThanksMessage))
            return render_to_response('pjweb/thanks.html', {
                'ThanksMessage': ThanksMessage,
                'LANGUAGES': settings.LANGUAGES,
                'step1': 'step1_inactive.png',
                'step2': 'step2_inactive.png',
                'step3': 'step3_active.png',
            })

    else:
        form = FeedbackForm()
        
    return render_to_response('pjweb/response.html', {
        'form': form,
        'mail': mail,
        'msg_lst': mail.message.split('\n'),
        'response_no': response_no,
        'LANGUAGES': settings.LANGUAGES,
        'step1': 'step1_inactive.png',
        'step2': 'step2_inactive.png',
        'step3': 'step3_inactive.png',
    })

