#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import re
from settings import *
from django import forms
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _, ugettext_lazy, ungettext, check_for_language
from django.core.mail import send_mail, EmailMessage
from parasykjiems.pjweb.models import Email, MailHistory
from parasykjiems.pjweb.forms import *
from pjutils.address_search import AddressSearch
from pjutils.insert_response import InsertResponse
from pjutils.declension import DeclensionLt
from django.utils import simplejson
import random
from django.contrib.sites.models import Site
from pjutils.uniconsole import *
import datetime
from cdb_lt_municipality.models import MunicipalityMember, Municipality
from cdb_lt_mps.models import ParliamentMember, Constituency, PollingDistrictStreet
from cdb_lt_civilparish.models import CivilParishMember, CivilParishStreet
from cdb_lt_seniunaitija.models import SeniunaitijaMember, SeniunaitijaStreet
from cdb_lt_streets.models import HierarchicalGeoData, LithuanianStreetIndexes
from django.db.models.query_utils import Q, Q
from django.utils.encoding import iri_to_uri
from pjutils.deprecated import deprecated
from cdb_lt_streets.searchInIndex import searchInIndex, deduceAddress, removeGenericPartFromStreet, removeGenericPartFromMunicipality
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from pjweb.forms import IndexForm, ContactForm


logger = logging.getLogger(__name__)

def is_odd(number):
    if number%2==1:
        return True
    else:
        return False



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
        logger.debug("%s %s %s %s %s" % (e.id, e.street, e.city, e.municipality, e.number))
    logger.debug("len %s " % len(found_entries))

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

    houseNumberEquals = Q(**{"%s__lte" % "numberFrom": house_number}) & \
        Q(**{"%s__gte" % "numberTo": house_number}) & \
        Q(**{"%s" % "numberOdd": isOdd})

    houseNumberIsNull = Q(**{"%s__isnull" % "numberFrom": True}) & \
        Q(**{"%s__isnull" % "numberTo": True})

    orQuery = houseNumberEquals | houseNumberIsNull

    query = query.filter(orQuery)
    return query




def findMPs(municipality = None, city = None, street = None, house_number = None):
    street = removeGenericPartFromStreet(street)
    municipality = removeGenericPartFromMunicipality(municipality)

    logging.info("searching for MP: street %s, city %s, municipality %s" % (street, city, municipality))

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
    logging.debug("found MPs in following constituency : %s" % (idList))
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
    logger.debug("choose_rep: municipality %s" % municipality)
    logger.debug("choose_rep: city %s" % city)
    logger.debug("choose_rep: street %s" % street)
    logger.debug("choose_rep: house_number %s" % house_number)

    parliament_members = findMPs(municipality, city, street, house_number)
    municipality_members = findMunicipalityMembers(municipality, city, street, house_number)
    civilparish_members = findCivilParishMembers(municipality, city, street, house_number)
    seniunaitija_members = findSeniunaitijaMembers(municipality, city, street, house_number)


    return render_to_response('pjweb/const.html', {
        'parliament_members': parliament_members,
        'municipality_members': municipality_members,
        'civilparish_members': civilparish_members,
        'seniunaitija_members': seniunaitija_members,
        'LANGUAGES': GlobalSettings.LANGUAGES,
        'step1': 'active-step',
        'step2': '',
        'step3': '',
    })


def json_lookup(request, queryset, field, limit=5, login_required=False):
    if login_required and not request.user.is_authenticated():
        return redirect_to_login(request.path)
    obj_list = []
    lookup = { '%s__icontains' % field: request.GET['query'],}
    for obj in queryset.filter(**lookup)[:limit]:
        obj_list.append({"id": obj.id, "name": getattr(obj, field)}) 
    object = {"ResultSet": { "total": str(limit), "Result": obj_list } }
    return HttpResponse(simplejson.dumps(object), mimetype='application/javascript')


def index(request):
    query_string = ' '
    address = {
        'found_entries': None,
        'found_geodata': None,
        'not_found': '',
        }
    lang = request.LANGUAGE_CODE
    if request.method == 'POST':
        form = IndexForm(request.POST)
        if form.is_valid():
            query_string = form.cleaned_data['address_input']
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
            'LANGUAGES': GlobalSettings.LANGUAGES,
            'lang_code': lang,
            'entered': query_string,
            'found_entries': address['found_entries'],
            'found_geodata': address['found_geodata'],
            'not_found': address['not_found'],
            'step1': 'active-step',
            'step2': '',
            'step3': '',
        })


def no_email(request, rtype, mp_id):
    insert = InsertResponse()
    representative = insert.get_rep(mp_id, rtype)
    NoEmailMsg = _('%(name)s %(surname)s email cannot be found in database.') % {
        'name':representative.name, 'surname':representative.surname
    }
    logger.debug('%s' % (NoEmailMsg))
    return render_to_response('pjweb/no_email.html', {
        'NoEmailMsg': NoEmailMsg,
        'LANGUAGES': GlobalSettings.LANGUAGES,
        'step1': '',
        'step2': 'active-step',
        'step3': '',
    })


def public_mails(request):
    all_mails = Email.objects.all().filter(public__exact=True, msg_type__exact='Question').exclude(msg_state__exact='NotConfirmed')
    mail_list = []
    
    for mail in all_mails:
        id = mail.id
        recipient_name = mail.recipient_name
        sender = mail.sender_name
        message = mail.message
        send_date = mail.mail_date.strftime("%Y-%m-%d %H:%M")
        answers = Email.objects.filter(answer_to=mail.id)
        if not answers:
            has_response = _('No')
        else:
            has_response = _('Yes')
        mail_dict = {'id':id,'recipient_name':recipient_name, 'sender':sender, 'message':message, 'send_date':send_date,'has_response':has_response}
        mail_list.append(mail_dict)
    
    paginator = Paginator(mail_list, 10) # Show 10 contacts per page
    # Make sure page request is an int. If not, deliver first page.
    try:
        page = int(request.GET.get('page', '1'))
    except ValueError:
        page = 1

    # If page request (9999) is out of range, deliver last page of results.
    try:
        mails = paginator.page(page)
    except (EmptyPage, InvalidPage):
        mails = paginator.page(paginator.num_pages)
        
    return render_to_response('pjweb/public_mails.html', {
        'all_mails': all_mails,
        'mails': mails,
        'mail_list': mail_list,
        'LANGUAGES': GlobalSettings.LANGUAGES,
        'step1': '',
        'step2': '',
        'step3': '',
    })


def about(request):
    return render_to_response('pjweb/about.html', {
        'LANGUAGES': GlobalSettings.LANGUAGES,
        'step1': '',
        'step2': '',
        'step3': '',
    })


def public(request, mail_id):
    mail = Email.objects.get(id=mail_id)
    responses = Email.objects.filter(answer_to__exact=mail_id)
    return render_to_response('pjweb/public.html', {
        'mail': mail,
        'responses': responses,
        'LANGUAGES': GlobalSettings.LANGUAGES,
        'step1': '',
        'step2': '',
        'step3': '',
    })


def smtp_error(request, rtype, mp_id, private=None):
    insert = InsertResponse()
    representative = insert.get_rep(mp_id, rtype)
    ErrorMessage = _(
        'Problem occurred. Your Email to %(name)s %(surname)s has not been sent. Please try again later.'
    ) % {
        'name':representative.name, 'surname':representative.surname
    }
    logger.debug('Error: %s' % (ErrorMessage))
    return render_to_response('pjweb/error.html', {
        'ErrorMessage': ErrorMessage,
        'LANGUAGES': GlobalSettings.LANGUAGES,
        'step1': '',
        'step2': '',
        'step3': 'active-step',
    })

def contact(request, rtype, mp_id):
    insert = InsertResponse()
    # find required representative
    receiver = insert.get_rep(mp_id, rtype)
    current_site = Site.objects.get_current()
    months = [
        _(u'January'),
        _(u'February'),
        _(u'March'),
        _(u'April'),
        _(u'May'),
        _(u'June'),
        _(u'July'),
        _(u'August'),
        _(u'September'),
        _(u'October'),
        _(u'November'),
        _(u'December')
    ]

    if not receiver.email:
        return HttpResponseRedirect('no_email')

    if request.method == 'POST':
        send = request.POST.has_key('send')
        form = ContactForm(data=request.POST)
        if form.is_valid():
            public = form.cleaned_data[u'public']
            publ = False
            if public=='public':
                publ = True
            sender_name = form.cleaned_data[u'sender_name']
            phone = form.cleaned_data[u'phone']
            message = form.cleaned_data[u'message']
            sender = form.cleaned_data[u'sender']
            response_hash = random.randrange(0, 1000000),

            response_hash = response_hash[0]

            recipients = [receiver.email]

            # if representative has no email - show message
            if not recipients[0]:
                logger.debug('%s %s has no email' % (receiver.name, receiver.surname))
                return HttpResponseRedirect('no_email')
            else:
                message_disp = message
                mail = Email(
                    sender_name = sender_name,
                    sender_mail = sender,
                    recipient_id = receiver.id,
                    recipient_type = rtype,
                    recipient_name = '%s %s' % (receiver.name, receiver.surname),
                    recipient_mail = recipients[0],
                    message = message,
                    msg_state = 'NotConfirmed',
                    msg_type = 'Question',
                    response_hash = response_hash,
                    public = publ,
                )
                if send:
                    print mail.message
                    mail.save()
                    reply_to = 'reply%s_%s@dev.parasykjiems.lt' % (mail.id, mail.response_hash)
                    # generate confirmation email message and send it
                    message = _('You sent an email to ')+ mail.recipient_name + _(' with text:\n\n')+ message_disp + _('\n\nYou must confirm this message by clicking link below:\n') + 'http://%s/confirm/%s/%s' % (current_site.domain, mail.id, mail.response_hash)
                    email = EmailMessage(u'Confirm your message %s' % sender_name, message, settings.EMAIL_HOST_USER,
                        [sender], [],
                        headers = {'Reply-To': reply_to})
                    email.send()
                    ThanksMessage = _('Thank you. This message must be confirmed. Please check your email.')
                    logger.debug('%s' % (ThanksMessage))
                    return render_to_response('pjweb/thanks.html', {
                        'ThanksMessage': ThanksMessage,
                        'LANGUAGES': GlobalSettings.LANGUAGES,
                        'step1': '',
                        'step2': '',
                        'step3': 'active-step',
                    })
            if not send:
                d = datetime.date.today()
                date_words = '%s %s %s' % (d.year, months[d.month-1], d.day)
                return render_to_response('pjweb/preview.html', {
                    'form': form,
                    'mp_id': mp_id,
                    'rtype': rtype,
                    'preview': mail,
                    'msg_lst': message_disp,
                    'representative': receiver,
                    'LANGUAGES': GlobalSettings.LANGUAGES,
                    'date_words': date_words,
                    'step1': '',
                    'step2': '',
                    'step3': 'active-step',
                })

    else:
        decl = DeclensionLt()
        form = ContactForm(initial={'message': _(u'Dear. Mr. %s, \n\n\n\nHave a nice day.') % decl.sauksm(receiver.name) })
        
    return render_to_response('pjweb/contact.html', {
        'form': form,
        'mp_id': mp_id,
        'rtype': rtype,
        'representative': receiver,
        'LANGUAGES': GlobalSettings.LANGUAGES,
        'step1': '',
        'step2': 'active-step',
        'step3': '',
    })


def confirm(request, mail_id, secret):
    mail = Email.objects.get(id=mail_id)
    if (int(mail_id)==mail.id) and (int(secret)==mail.response_hash):
        print mail.id
        ConfirmMessage = _('Thank you. Your message has been sent.')

        # update message state 
        mail.msg_state = 'Confirmed'

        # determine where to send email
        domain = GlobalSettings.MAIL_SERVER
        #reply_to = 'reply%s_%s@dev.parasykjiems.lt' % (mail.id, mail.response_hash)
        reply_to = 'reply%s_%s@%s' % (mail.id, mail.response_hash, domain)

        # assigning message to email
        message = mail.message

        # if message is private - clear it in db
        if not mail.public:
            message = mail.message
            mail.message = ''

        # save message state to db
        mail.save()

        if (GlobalSettings.mail.sendEmailToRepresentatives == "sendToRepresentatives"):
            recipients = [mail.recipient_mail]
        else:
            recipients = GlobalSettings.mail.sendEmailToRepresentatives


        # send an actual email message to government representative
        email = EmailMessage(u'Gavote laišką nuo %s' % mail.sender_name, message, settings.EMAIL_HOST_USER,
            recipients, [],
            headers = {'Reply-To': reply_to})
        email.send()

        # store in email history status of message, so we can know that this message got sent
        history = MailHistory(
            sender = mail.sender_mail,
            recipient = recipients[0],
            mail = mail,
            mail_state = 'Sent',
        )
        history.save()

        # finished confirminging, just render response
    else:
        # render response with failed message
        ConfirmMessage = _('Sorry, but your message could not be confirmed.')

    logger.debug('%s' % (ConfirmMessage))
    return render_to_response('pjweb/confirm.html', {
        'ConfirmMessage': ConfirmMessage,
        'LANGUAGES': GlobalSettings.LANGUAGES,
        'step1': '',
        'step2': '',
        'step3': '',
    })


def feedback(request):

    if request.method == 'POST':
        form = FeedbackForm(data=request.POST)
        if form.is_valid():
            message = form.cleaned_data[u'message']
            sender = 'Concerned citizen'
            recipients = [GlobalSettings.mail.feedbackEmail]
            email = EmailMessage(u'Pastaba dėl parašykjiems.lt', message, settings.EMAIL_HOST_USER,
                recipients, [])
            email.send()
            ThanksMessage = _('Thank you. Your message has been sent.')
            logger.debug('%s' % (ThanksMessage))
            return render_to_response('pjweb/thanks.html', {
                'ThanksMessage': ThanksMessage,
                'LANGUAGES': GlobalSettings.LANGUAGES,
                'step1': '',
                'step2': '',
                'step3': '',
            })

    else:
        form = FeedbackForm()
        
    return render_to_response('pjweb/feedback.html', {
        'form': form,
        'LANGUAGES': GlobalSettings.LANGUAGES,
        'step1': '',
        'step2': '',
        'step3': '',
    })


def stats(request):
    period_string = ''
    if request.method == 'POST':
        form = PeriodSelectForm(data=request.POST)
        if form.is_valid():
            date_from = form.cleaned_data['date_from']
            date_to = form.cleaned_data['date_to']
            questions = len(Email.objects.filter(
                msg_type__iexact='Question', msg_state__iexact='Confirmed',
                mail_date__gte=date_from,mail_date__lte=date_to
            ))
            responses = len(Email.objects.filter(
                msg_type__iexact='Response', mail_date__gte=date_from,mail_date__lte=date_to
            ))
            new_addresses = len(Email.objects.filter(
                answer_to__exact=None, mail_date__gte=date_from,mail_date__lte=date_to
            ).values('sender_mail').distinct())
            period_string = _('In selected period (from %(from)s to %(to)s):') % {'from':date_from, 'to':date_to}
            stats = [
                _('Questions sent: %s') % questions,
                _('Answers got: %s') % responses,
                _('New users: %s') % new_addresses,
            ]
            return render_to_response('pjweb/stats.html', {
                'period_string': period_string,
                'stats': stats,
                'form': form,
                'LANGUAGES': GlobalSettings.LANGUAGES,
                'step1': '',
                'step2': '',
                'step3': '',
            })

    else:
        form = PeriodSelectForm()
        
    return render_to_response('pjweb/stats.html', {
        'period_string': period_string,
        'form': form,
        'LANGUAGES': GlobalSettings.LANGUAGES,
        'step1': '',
        'step2': '',
        'step3': '',
    })


def response(request, mail_id, response_no):
    mail = Email.objects.get(id=mail_id)
    insert = InsertResponse()
    responder = insert.get_rep(mail.recipient_id, mail.recipient_type)
    if int(mail.response_hash)==int(response_no) and request.method == 'POST':
        form = FeedbackForm(data=request.POST)
        if form.is_valid():
            message = form.cleaned_data[u'message']
            sender = responder.email
            recipients = mail.sender

            response = Email(
                sender_name = mail.recipient_name,
                sender_mail = responder.email,
                recipient_id = mail.recipient_id,
                recipient_type = mail.recipient_type,
                recipient_name = mail.sender_name,
                recipient_mail = mail.sender_mail,
                message = message,
                msg_type = 'Response',
                answer_to = mail.id,
                public = mail.public,
            )
            response.save()
            ThanksMessage = _('Thank you. Your response has been posted.')
            logger.debug('%s' % (ThanksMessage))
            return render_to_response('pjweb/thanks.html', {
                'ThanksMessage': ThanksMessage,
                'LANGUAGES': GlobalSettings.LANGUAGES,
                'step1': '',
                'step2': '',
                'step3': 'active-step',
            })

    else:
        form = FeedbackForm()
        
    return render_to_response('pjweb/response.html', {
        'form': form,
        'mail': mail,
        'msg_lst': mail.message.split('\n'),
        'response_no': response_no,
        'LANGUAGES': GlobalSettings.LANGUAGES,
        'step1': '',
        'step2': '',
        'step3': '',
    })


def set_language(request, lang_code):
    """
    Patched for Get method
    """
    next = request.REQUEST.get('next', None)
    if not next:
        next = '/'
    response = HttpResponseRedirect(next)
    if lang_code and check_for_language(lang_code):
        if hasattr(request, 'session'):
            request.session['django_language'] = lang_code
        else:
            response.set_cookie(settings.LANGUAGE_COOKIE_NAME, lang_code)
    return response

