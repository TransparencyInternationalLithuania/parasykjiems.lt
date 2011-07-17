#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
from django.contrib.auth.views import redirect_to_login
from pjweb.email.emailTemplates import renderEmailTemplate
from settings import GlobalSettings
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import render_to_response
from django.utils.translation import ugettext as _, check_for_language
from django.core.mail import EmailMessage
from contactdb.models import PersonPosition
from pjweb.models import Email, MailHistory
import pjweb.forms as forms
from pjutils.insert_response import InsertResponse
from pjutils.declension import DeclensionLt
from django.utils import simplejson
import random
from django.contrib.sites.models import Site
import datetime
from django.utils.encoding import iri_to_uri
from django.core.paginator import Paginator, InvalidPage, EmptyPage
from territories.houseNumberUtils import removeCornerFromHouseNumber
from territories.searchInIndex import deduceAddress, searchInIndex
from territories.searchMembers import findPersonPositions
from cdb_lt.management.commands.createMembers import loadInstitutionDescriptions
import settings


logger = logging.getLogger(__name__)

def logAddressQueryToFile(queryString):
    if GlobalSettings.logAddressesToFile is None:
        return
    with open(GlobalSettings.logAddressesToFile, "a") as f:
        s = u"%s\n" % queryString
        f.write(s.encode('utf-8'))


def searchInStreetIndex(query_string):
    """ Searches throught street index and returns municipality / city / street/ house number
    Additionally returns more data for rendering in template"""

    logger.debug("query_string %s" % query_string)
    found_geodata = None
    not_found = ''


    logAddressQueryToFile(query_string)


    addressContext = deduceAddress(query_string)
    addressContext.number = removeCornerFromHouseNumber(addressContext.number)


    found_entries = searchInIndex(municipality= addressContext.municipality, city= addressContext.city,
                                  street= addressContext.street)

    # construct final uriss
    for f in found_entries:
        # attach house numbers
        f.number = addressContext.number

        # construct a final uri, and attach it
        if (f.civilParish is not None) and (f.civilParish != u"") and ((f.street is None) or (f.street == u"")):
            iri = "/choose_rep_civilparish/%s/%s/%s/" % (f.municipality, f.civilParish, f.city_genitive)
        elif (f.number is not None) and (f.number != ""):
            iri = "/choose_rep/%s/%s/%s/%s/" % (f.municipality, f.city_genitive, f.street, f.number)
        elif (f.street is not None and f.street != u""):
            iri = "/choose_rep/%s/%s/%s/" % (f.municipality, f.city_genitive, f.street)
        else:
            iri = "/choose_rep/%s/%s/" % (f.municipality, f.city_genitive)
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


def choose_representative_civil_parish(request, municipality = None, civilParish = None, city = None):
    return choose_representative_internal(request=request, municipality=municipality, civilParish=civilParish, city=city)

def choose_representative(request, municipality = None, city = None, street = None, house_number = None):
    return choose_representative_internal(request=request, municipality=municipality, city=city, street=street, house_number= house_number)

def choose_representative_internal(request, municipality = None, civilParish = None, city = None, street = None, house_number = None):
    # check if we have a valid referrer
    logger.debug("choose_rep: municipality %s" % municipality)
    logger.debug("choose_rep: city %s" % city)
    logger.debug("choose_rep: street %s" % street)
    logger.debug("choose_rep: house_number %s" % house_number)

    #cityGenitive = city
    #city = getCityNominative(municipality, city, street)

    #additionalKeys = {"city_genitive" : cityGenitive}
    additionalKeys = {}
    personPositions = findPersonPositions(municipality=municipality, civilParish=civilParish, city=city, street=street, house_number=house_number, **additionalKeys)

    institutionDescriptions = loadInstitutionDescriptions()
    for p in personPositions:
        p.institutionDescription = institutionDescriptions[p.institution.institutionType.code]

    return render_to_response('pjweb/const.html', {
        'personPositions': personPositions,
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


def renderIndexPage(request, form = None, query_string = "", address = None):
    if form is None:
        form = forms.IndexForm(request.POST)

    lang = request.LANGUAGE_CODE
    if address is None:
        address = {
        'found_entries': None,
        'found_geodata': None,
        'not_found': '',
        }
    return render_to_response("pjweb/searchPlugins/territory/index.html", {
        'form': form,
        'lang_code': lang,
        'entered': query_string,
        'found_entries': address['found_entries'],
        'found_geodata': address['found_geodata'],
        'not_found': address['not_found'],
        'step1': 'active-step',
        'step2': '',
        'step3': '',
    })


def index(request):
    query_string = ' '
    address = {
        'found_entries': None,
        'found_geodata': None,
        'not_found': '',
        }

    if request.method == 'GET':
        form = forms.IndexForm()
        return renderIndexPage(request, form)

    form = forms.IndexForm(request.POST)
    query_string = ""
    if form.is_valid():
        query_string = form.cleaned_data['address_input']
        
    if query_string == None or query_string == u"":
        return renderIndexPage(request, form)

    address = searchInStreetIndex(query_string)

    if address['found_entries'] and len(address['found_entries'])==1:
        url = address['found_entries'][0].url
        return HttpResponseRedirect(url)
    else:
        return renderIndexPage(request, form, address = address)



def no_email(request, rtype, mp_id):
    representative = PersonPosition.objects.get(id=mp_id)
    NoEmailMsg = _('%(name)s %(surname)s email cannot be found in database.') % {
        'name':representative.person.name, 'surname':representative.person.surname
    }
    logger.debug('%s' % (NoEmailMsg))
    return render_to_response('pjweb/no_email.html', {
        'NoEmailMsg': NoEmailMsg,
        'step1': '',
        'step2': 'active-step',
        'step3': '',
    })


class PublicMailListViewException(Exception):
    pass

class PublicMailListView:

    def __getitem__(self, k):
        if type(k) is not slice:
            raise PublicMailListViewException()
        all_mails = Email.objects.all().filter(public__exact=True, msg_type__exact='Question').exclude(msg_state__exact='NotConfirmed').order_by('-mail_date')
        all_mails = all_mails[k.start: k.stop]
        all_mails = list(all_mails)

        # pre-load and attach personPosition objects
        personPositionIds = [e.recipient_id for e in all_mails]
        personPositions = PersonPosition.objects.all().filter(id__in = personPositionIds).select_related('institution')
        personPositionsDict = dict((p.id, p) for p in list(personPositions))

        for email in all_mails:
            email.personPosition = personPositionsDict[email.recipient_id]

        # pre-load whether email has answer
        mailIds = [mail.id for mail in all_mails]
        answers = Email.objects.filter(answer_to__in= mailIds).values('id', 'answer_to')
        dictAnswers = dict([(a['answer_to'], a['answer_to']) for a in answers])

        # attach whether we have answer
        hasnot_response = _('No')
        has_response = _('Yes')
        for email in all_mails:
            if dictAnswers.has_key(email.id):
                email.has_response = has_response
            else:
                email.has_response = hasnot_response


        return all_mails

    def count(self):
        return Email.objects.all().filter(public__exact=True, msg_type__exact='Question').exclude(msg_state__exact='NotConfirmed').count()

def public_mails(request):
    mail_list = PublicMailListView()

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
        'mails': mails,
        'step1': '',
        'step2': '',
        'step3': '',
    })


def about(request):
    return render_to_response('pjweb/about.html', {
        'step1': '',
        'step2': '',
        'step3': '',
    })


def public(request, mail_id):
    try:
        mail = Email.objects.get(id=mail_id)
    except Email.DoesNotExist:
        raise Http404()


    responses = list(Email.objects.filter(answer_to__exact=mail_id))
    responses = [mail] + list(responses)
    personPositionsIds = [r.recipient_id for r in responses]
    personPositions = PersonPosition.objects.filter(id__in = personPositionsIds).select_related('institution')
    personPositionDict = dict([(pp.id, pp) for pp in personPositions])

    current_site = Site.objects.get_current()
    # attachment paths are relative in DB
    # construct real attachment paths

    for r in responses:
        if r.attachment_path is not None:
            path = "%s/%s" % (GlobalSettings.ATTACHMENTS_MEDIA_PATH, r.attachment_path)
            path = path.replace("\\", "/")
            r.attachment_path = "http://%s/%s" % (current_site.domain, path)

        if r.msg_type == 'Question':
            r.recipientPersonPosition = personPositionDict.get(r.recipient_id)
        elif r.msg_type == 'Response':
            r.sendersPersonPosition = personPositionDict.get(r.recipient_id)

    return render_to_response('pjweb/public.html', {
        'mail': mail,
        'responses': responses,
        'step1': '',
        'step2': '',
        'step3': '',
    })

def redirectToIndex():
    url = "/"
    return HttpResponseRedirect(url)
    
def contact(request, rtype, mp_id):
    current_site = Site.objects.get_current()

    # find required representative
    try:
        receiver = PersonPosition.objects.get(id=mp_id)
    except PersonPosition.DoesNotExist:
        return redirectToIndex()

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
        form = forms.ContactForm(data=request.POST)
        if form.is_valid():
            public = form.cleaned_data[u'public']
            publ = public=='public'
            sender_name = form.cleaned_data[u'sender_name']
            message = form.cleaned_data[u'message']
            sender = form.cleaned_data[u'sender']
            subject = form.cleaned_data[u'subject']
            response_hash = random.randrange(0, 1000000)

            # if representative has no email - show message
            if not receiver.email:
                logger.debug('%s has no email' % receiver)
                return HttpResponseRedirect('no_email')
            else:
                message_disp = message
                mail = Email(
                    sender_name = sender_name,
                    sender_mail = sender,
                    subject = subject,
                    recipient_id = receiver.id,
                    recipient_type = rtype,
                    recipient_name = receiver.person.fullName,
                    recipient_mail = receiver.email,
                    message = message,
                    msg_state = 'NotConfirmed',
                    msg_type = 'Question',
                    response_hash = response_hash,
                    public = publ,
                )
                if send:
                    mail.save()  
                    reply_to = '%s%s-%s@%s' % (GlobalSettings.DefaultMailPrefix, mail.id, mail.response_hash, GlobalSettings.mail.IMAP.EMAIL_HOST)

                    confirm_link = ("http://%s/confirm/%s/%s") % (current_site.domain, mail.id, mail.response_hash)
                    emailTemplateParams = {'current_site' : current_site, 'mail' : mail, 'confirm_link': confirm_link}
                    message = renderEmailTemplate(u"email_confirmation.txt", emailTemplateParams)

                    email = EmailMessage(
                        subject = _(u'Confirm your message, %s') % sender_name,
                        body = message,
                        from_email = GlobalSettings.mail.SMTP.CONFIRMATION_EMAIL_SENT_FROM,
                        to = [sender],
                        bcc = [], 
                        headers = {'Reply-To': reply_to},
                    )
                    email.send()
                    ThanksMessage = _('Thank you. This message must be confirmed. Please check your email.')
                    return render_to_response('pjweb/thanks.html', {
                        'ThanksMessage': ThanksMessage,
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
                    'date_words': date_words,
                    'step1': '',
                    'step2': '',
                    'step3': 'active-step',
                })

    else:
        decl = DeclensionLt()
        form = forms.ContactForm(initial={'message': _(u'Dear. Mr. %s, \n\n\n\nHave a nice day.') % decl.sauksm(receiver.person.name) })
        
    return render_to_response('pjweb/contact.html', {
        'form': form,
        'mp_id': mp_id,
        'rtype': rtype,
        'representative': receiver,
        'step1': '',
        'step2': 'active-step',
        'step3': '',
    })

def confirmMessageAndSendEmailToRepresentative(mail):
    current_site = Site.objects.get_current()

    # compile an actual message
    mail.response_url = "http://%s/public/%s/" % (current_site.domain, mail.id)
    emailTemplateParams =  {'current_site' : current_site, 'mail' : mail, 'messageBody' :mail.message}
    message = renderEmailTemplate(u"email_to_representative.txt", emailTemplateParams)

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
        'step1': '',
        'step2': '',
        'step3': '',
    })


def feedback(request):

    if request.method == 'POST':
        form = forms.FeedbackForm(data=request.POST)
        if form.is_valid():
            message = form.cleaned_data[u'message']
            subject = form.cleaned_data[u'subject']
            emailFrom = form.cleaned_data[u'emailFrom']
            recipients = GlobalSettings.mail.feedbackEmail
            email = EmailMessage(subject=subject, body=message, from_email=settings.EMAIL_HOST_USER,
                to=recipients, bcc=[], headers={'Reply-To': emailFrom})
            email.send()

            ThanksMessage = _('Thank you for your feedback. You will be contacted shortly.')
            logger.debug('%s' % (ThanksMessage))
            logger.info("feedback email sent to '%s'" % recipients)
            return render_to_response('pjweb/feedback/feedback_sent.html', {
                'ThanksMessage': ThanksMessage,
                'step1': '',
                'step2': '',
                'step3': '',
            })


    else:
        form = forms.FeedbackForm()
        
    return render_to_response('pjweb/feedback/feedback.html', {
        'form': form,
        'step1': '',
        'step2': '',
        'step3': '',
    })


def stats(request):
    period_string = ''
    if request.method == 'POST':
        form = forms.PeriodSelectForm(data=request.POST)
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
                'step1': '',
                'step2': '',
                'step3': '',
            })

    else:
        form = forms.PeriodSelectForm()
        
    return render_to_response('pjweb/stats.html', {
        'period_string': period_string,
        'form': form,
        'step1': '',
        'step2': '',
        'step3': '',
    })


def response(request, mail_id, response_no):
    mail = Email.objects.get(id=mail_id)
    responder = PersonPosition.objects.get(id=mail.recipient_id)
    if int(mail.response_hash)==int(response_no) and request.method == 'POST':
        form = forms.FeedbackForm(data=request.POST)
        if form.is_valid():
            message = form.cleaned_data[u'message']

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
                'step1': '',
                'step2': '',
                'step3': 'active-step',
            })

    else:
        form = forms.FeedbackForm()
        
    return render_to_response('pjweb/response.html', {
        'form': form,
        'mail': mail,
        'msg_lst': mail.message.split('\n'),
        'response_no': response_no,
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

