#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import re
from django.template import loader
from cdb_lt_streets.searchMembers import findMPs, findMunicipalityMembers, findCivilParishMembers, findSeniunaitijaMembers
from cdb_lt_streets.streetUtils import getCityNominative
from settings import *
from django import forms
from django.http import HttpResponseRedirect, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response, redirect
from django.utils.translation import ugettext as _, ugettext_lazy, ungettext, check_for_language
from django.core.mail import send_mail, EmailMessage
from pjweb.models import Email, MailHistory
from pjweb.forms import *
from pjutils.address_search import AddressSearch
from pjutils.insert_response import InsertResponse
from pjutils.declension import DeclensionLt
from django.utils import simplejson
import random
from django.contrib.sites.models import Site
from pjutils.uniconsole import *
import datetime
from django.utils.encoding import iri_to_uri
from cdb_lt_streets.searchInIndex import searchInIndex, deduceAddress
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from pjweb.forms import IndexForm, ContactForm


logger = logging.getLogger(__name__)

def searchInStreetIndex(query_string):
    """ Searches throught street index and returns municipality / city / street/ house number
    Additionally returns more data for rendering in template"""

    logger.debug("query_string %s" % query_string)
    found_geodata = None
    not_found = ''

    addressContext = deduceAddress(query_string)
    found_entries = searchInIndex(addressContext)

    # construct final uriss
    for f in found_entries:
        # attach house numbers
        f.number = addressContext.number

        # construct a final uri, and attach it
        if (f.number is not None) and (f.number != ""):
            iri = "/pjweb/choose_rep/%s/%s/%s/%s/" % (f.municipality, f.city_genitive, f.street, f.number)
        elif (f.street is not None and f.street != u""):
            iri = "/pjweb/choose_rep/%s/%s/%s/" % (f.municipality, f.city_genitive, f.street)
        else:
            iri = "/pjweb/choose_rep/%s/%s/" % (f.municipality, f.city_genitive)
        uri = iri_to_uri(iri)
        f.url = uri


    for e in found_entries:
        logger.debug("%s %s %s %s %s" % (e.id, e.street, e.city_genitive, e.municipality, e.number))
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



def choose_representative(request, municipality = None, city = None, street = None, house_number = None):
    # check if we have a valid referrer
    current_site = Site.objects.get_current()
    if (DEBUG == False):
        referer = request.META.get('HTTP_REFERER', '')
        host = 'http://%s/' % current_site.domain
        if not referer or (referer != host):
            return HttpResponseRedirect('/')
    logger.debug("choose_rep: municipality %s" % municipality)
    logger.debug("choose_rep: city %s" % city)
    logger.debug("choose_rep: street %s" % street)
    logger.debug("choose_rep: house_number %s" % house_number)

    #cityGenitive = city
    #city = getCityNominative(municipality, city, street)

    #additionalKeys = {"city_genitive" : cityGenitive}
    additionalKeys = {}
    parliament_members = findMPs(municipality, city, street, house_number, **additionalKeys)
    municipality_members = findMunicipalityMembers(municipality, city, street, house_number, **additionalKeys)
    civilparish_members = findCivilParishMembers(municipality, city, street, house_number, **additionalKeys)
    seniunaitija_members = findSeniunaitijaMembers(municipality, city, street, house_number, **additionalKeys)


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
    all_mails = Email.objects.all().filter(public__exact=True, msg_type__exact='Question').exclude(msg_state__exact='NotConfirmed').order_by('-mail_date')
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
    current_site = Site.objects.get_current()
    # attachment paths are relative in DB
    # construct real attachment paths
    responses = list(responses)
    for r in responses:
        if (r.attachment_path is not None):
            path = "%s/%s" % (GlobalSettings.ATTACHMENTS_MEDIA_PATH, r.attachment_path)
            path = path.replace("\\", "/")
            r.attachment_path = "http://%s/%s" % (current_site.domain, path)
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
    current_site = Site.objects.get_current()
    # check if we have a valid referrer
    if (DEBUG == False):
        referer = request.META.get('HTTP_REFERER', '')
        host = 'http://%s/' % current_site.domain
        if not referer or (current_site.domain not in referer):
            return HttpResponseRedirect('/')

    # find required representative
    receiver = insert.get_rep(mp_id, rtype)
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
                    reply_to = '%s%s_%s@%s' % (GlobalSettings.DefaultMailPrefix, mail.id, mail.response_hash, GlobalSettings.mail.IMAP.EMAIL_HOST)
                    # generate confirmation email message and send it
                    confirm_link = ("http://%s/confirm/%s/%s") % (current_site.domain, mail.id, mail.response_hash)
                    line1 = _(u"Hello,")
                    line2 = _(u"in %(domain)s from Your address(%(sender)s) was written a leter to a representative.") % {'domain':current_site.domain, 'sender':sender}
                    line3 = _(u"Please confirm, that You want to send this message. If a letter was written not by You, it won't be sent without Your confirmation.")
                    line4 = _(u"If You suspect abuse, please write an email to abuse@parasykjiems.lt")
                    line5 = _(u"Your message:")
                    line6 = _(u"Receiver: %s.") % mail.recipient_name
                    endline = _(u"Send this email by clicking on link below:\n\n %s") % confirm_link


#                    languageId = "lt"
#                    messsage = render_to_string("mail_body.txt")

                    from_email = GlobalSettings.mail.SMTP.CONFIRMATION_EMAIL_SENT_FROM

                    message = line1 + "\n\n" + line2 + "\n\n" + line3 + "\n\n" + line4 + "\n\n" + line5 + "\n\n" + line6 + "\n\n" + message_disp + "\n\n" + endline
#                    _('You sent an email to ')+ mail.recipient_name + _(' with text:\n\n')+ message_disp + _('\n\nYou must confirm this message by clicking link \below:\n') + 'http://%s/confirm/%s/%s' % (current_site.domain, mail.id, mail.response_hash)
                    email = EmailMessage(subject=_(u'Confirm your message %s') % sender_name, body=message, from_email=from_email,
                        to=[sender], bcc=[], 
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

def confirmMessageAndSendEmailToRepresentative(mail):
    current_site = Site.objects.get_current()

    # compile an actual message
    mail.response_url = "http://%s/pjweb/public/%s/" % (current_site.domain, mail.id)
    message = loader.render_to_string('pjweb/emails/email_to_representative.txt', {
        'current_site' : current_site,
        'mail' : mail,
        'messageBody' :mail.message
    })

    # checking whether emails must be forwarded to some specific address
    # or to real representative addresses
    recipients = GlobalSettings.mail.sendEmailToRepresentatives
    if GlobalSettings.mail.sendEmailToRepresentatives == "sendToRepresentatives":
        recipients = [mail.recipient_mail]
    logger.info("sending email to these recipients: %s" % recipients)


    composition = GlobalSettings.mail.composition_backends[0]
    # determine reply address
    reply_to = composition.getReplyTo(mail)

    from_email=GlobalSettings.mail.SMTP.REPRESENTATIVE_EMAIL_SENT_FROM
    subject = composition.getSubject(mail)

    # send an actual email message to government representative
    email = EmailMessage(subject=subject, body=message, from_email=from_email,
        to=recipients, bcc=[],
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


    # Mark finally that message has been finally confirmed and sent to representative
    # update message state.  Do this only after email has been sent, so that email fail error
    # would not mark this message as confirmed prematurely
    mail.msg_state = 'Confirmed'

    # if message is private - clear it in db, since even if it was private,
    # it has been saved in DB so that we could confirm it later and send it
    if not mail.public:
        mail.message = ''

    # save message state to db
    mail.save()


def confirm(request, mail_id, secret):
    """ When user clicks on confirmation link in his email,
        we set message state as confirmed, compile a standard message header and
        send email to final recipient (usually government representative)  """
    mail = Email.objects.get(id=mail_id)

    # check if email was already confirmed or not
    if mail.msg_state != 'Confirmed':
        # check if provided hash does match with our own hash stored in db
        if (int(mail_id)==mail.id) and (int(secret)==mail.response_hash):
            # save message State as confirmed, and send email to representative
            confirmMessageAndSendEmailToRepresentative(mail)
            ConfirmMessage = _('Thank you. Your message has been sent.')
        else:
            # render response with failed message
            ConfirmMessage = _('Sorry, but your message could not be confirmed.')
    else:
        # this message was already confirmed, so display some info for that
        ConfirmMessage = _("Your message was already confirmed")

    logger.debug('%s' % (ConfirmMessage))
    return render_to_response('pjweb/confirm.html', {
        'ConfirmMessage': ConfirmMessage,
        'is_email_public': mail.public,
        'public_email_id' : mail.id,
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

